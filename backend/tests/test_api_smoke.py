import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient

from app.db.session import Base, engine
from app.main import app

RENT_TEXT = "Cap annual rent increases at 3% in urban areas to protect renters."
RENT2_TEXT = "Require landlords to register rents and limit increases to inflation."


def _depths(children):
    orders = set()

    def walk(nodes):
        for n in nodes:
            orders.add(n["order"])
            walk(n.get("children", []) or [])

    walk(children or [])
    return orders


def test_api_smoke():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    c = TestClient(app)
    assert c.get("/healthz").json() == {"ok": True}

    # empty policy_text -> 400
    r = c.post(
        "/api/policy/submit",
        json={"policy_text": "   ", "jurisdiction": "Test City", "policy_domain": "housing"},
    )
    assert r.status_code == 400, r.text

    r = c.post(
        "/api/policy/submit",
        json={
            "policy_text": RENT_TEXT,
            "jurisdiction": "Test City",
            "policy_domain": "housing",
            "context": "rental market",
            "target_demographic": "renters",
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    sid = body["submission_id"]
    assert body["model_id"]
    assert len(body["effects"]) >= 3

    r = c.get(f"/api/policy/{sid}/impact")
    assert r.status_code == 200, r.text
    tree = r.json()
    assert tree["model_id"] == body["model_id"]
    assert "submission" in tree
    children = tree["children"]
    assert isinstance(children, list) and len(children) >= 1
    assert {1, 2, 3} <= _depths(children)
    # nested: order1 has children order2 which has children order3
    o1 = [n for n in children if n["order"] == 1]
    assert o1 and all(n.get("children") for n in o1)
    for n1 in o1:
        for n2 in n1["children"]:
            assert n2["order"] == 2
            assert n2.get("children")
            for n3 in n2["children"]:
                assert n3["order"] == 3

    for path in ("demographics", "stakeholders", "analogies"):
        r = c.get(f"/api/policy/{sid}/{path}")
        assert r.status_code == 200, r.text
        rows = r.json()
        assert isinstance(rows, list) and len(rows) >= 1, path

    r = c.post(
        "/api/policy/submit",
        json={
            "policy_text": RENT2_TEXT,
            "jurisdiction": "Test City",
            "policy_domain": "housing",
        },
    )
    assert r.status_code == 200, r.text
    sid2 = r.json()["submission_id"]

    r = c.post("/api/policy/compare", json={"a_id": sid, "b_id": sid2})
    assert r.status_code == 200, r.text
    rows = r.json()
    rows = rows["rows"] if isinstance(rows, dict) and "rows" in rows else rows
    assert isinstance(rows, list) and len(rows) >= 1
    for row in rows:
        assert row["verdict"] in ("same", "contrast", "only_a", "only_b")
        assert "dimension" in row and "a" in row and "b" in row

    r = c.get("/api/policy/history")
    assert r.status_code == 200, r.text
    hist = r.json()
    assert isinstance(hist, list) and len(hist) >= 2
    ids = {h_item["id"] for h_item in hist}
    assert {sid, sid2} <= ids

    r = c.delete(f"/api/policy/{sid2}")
    assert r.status_code == 200, r.text
    r = c.get(f"/api/policy/{sid2}/impact")
    assert r.status_code == 404, r.text
