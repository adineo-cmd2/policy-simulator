from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.demographic_impact import DemographicImpact
from app.models.effect_node import EffectNode
from app.models.historical_analogy import HistoricalAnalogy
from app.models.impact_model import ImpactModel
from app.models.policy_submission import PolicySubmission
from app.models.stakeholder_record import StakeholderRecord
from app.models.user import User
from app.schemas.policy import PolicySubmitIn, PolicySubmitOut
from app.services import modelling_pipeline

router = APIRouter()

DOMAINS = {
    "healthcare",
    "housing",
    "taxation",
    "environment",
    "education",
    "labour",
    "trade",
    "general",
}


class CompareIn(BaseModel):
    a_id: int
    b_id: int


def _own_submission(db: Session, user: User, sid: int) -> PolicySubmission:
    s = db.query(PolicySubmission).filter(
        PolicySubmission.id == sid,
        PolicySubmission.user_id == user.id,
    ).first()
    if not s:
        raise HTTPException(status_code=404, detail="Submission not found")
    return s


def _model_for(db: Session, submission_id: int) -> ImpactModel | None:
    return db.query(ImpactModel).filter(
        ImpactModel.submission_id == submission_id
    ).first()


def _node_dict(n: EffectNode) -> dict:
    return {
        "id": n.id,
        "model_id": n.model_id,
        "parent_id": n.parent_id,
        "order": n.order,
        "title": n.title,
        "detail": n.detail,
        "domain_area": n.domain_area,
        "magnitude": n.magnitude,
        "direction": n.direction,
        "confidence": n.confidence,
        "analogy": n.analogy or "",
    }


@router.post("/submit", response_model=PolicySubmitOut)
def submit(body: PolicySubmitIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not (body.policy_text or "").strip():
        raise HTTPException(status_code=400, detail="policy_text required")
    domain = (body.policy_domain or "").lower().strip() or "general"
    if domain not in DOMAINS:
        domain = "general"
    jurisdiction = body.jurisdiction or ""
    context = body.context or ""
    if body.target_demographic:
        context = f"{context} [target: {body.target_demographic}]" if context else f"[target: {body.target_demographic}]"
    result = modelling_pipeline.run_model(
        db, user.id, body.policy_text, jurisdiction, domain, context
    )
    return PolicySubmitOut(
        submission_id=result["submission_id"],
        model_id=result["model_id"],
        effects=result["effects"],
    )


@router.post("/compare")
def compare(body: CompareIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    sa = _own_submission(db, user, body.a_id)
    sb = _own_submission(db, user, body.b_id)
    ma = _model_for(db, sa.id)
    mb = _model_for(db, sb.id)
    na = db.query(EffectNode).filter(EffectNode.model_id == ma.id).all() if ma else []
    nb = db.query(EffectNode).filter(EffectNode.model_id == mb.id).all() if mb else []

    def key(n: EffectNode):
        return (n.order, n.domain_area or "")

    map_a = {key(n): n for n in na}
    map_b = {key(n): n for n in nb}
    rows = []
    for k in sorted(set(map_a) | set(map_b)):
        order, area = k
        ea = map_a.get(k)
        eb = map_b.get(k)
        dimension = f"{order}:{area}"

        def summ(n: EffectNode | None):
            if n is None:
                return None
            return {
                "id": n.id,
                "title": n.title,
                "direction": n.direction,
                "magnitude": n.magnitude,
                "domain_area": n.domain_area,
                "order": n.order,
            }

        if ea is not None and eb is not None:
            verdict = "same" if ea.direction == eb.direction else "contrast"
        elif ea is not None:
            verdict = "only_a"
        else:
            verdict = "only_b"
        rows.append({"dimension": dimension, "a": summ(ea), "b": summ(eb), "verdict": verdict})
    return rows


@router.get("/history")
def history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    out = []
    subs = db.query(PolicySubmission).filter(
        PolicySubmission.user_id == user.id
    ).order_by(PolicySubmission.id).all()
    for s in subs:
        m = _model_for(db, s.id)
        count = db.query(EffectNode).filter(EffectNode.model_id == m.id).count() if m else 0
        out.append(
            {
                "id": s.id,
                "domain": s.policy_domain,
                "policy_domain": s.policy_domain,
                "jurisdiction": s.jurisdiction,
                "effects": count,
                "date": None,
            }
        )
    return out


@router.get("/{sid}/impact")
def impact(sid: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = _own_submission(db, user, sid)
    m = _model_for(db, s.id)
    nodes = db.query(EffectNode).filter(EffectNode.model_id == m.id).order_by(EffectNode.id).all() if m else []
    by_parent: dict = {}
    for n in nodes:
        by_parent.setdefault(n.parent_id, []).append(n)

    def build(n: EffectNode) -> dict:
        d = _node_dict(n)
        d["children"] = [build(ch) for ch in by_parent.get(n.id, [])]
        return d

    children = [build(n) for n in by_parent.get(None, [])]
    return {
        "model_id": m.id if m else None,
        "submission": {
            "id": s.id,
            "policy_domain": s.policy_domain,
            "jurisdiction": s.jurisdiction,
            "policy_text": s.policy_text,
        },
        "children": children,
    }


@router.get("/{sid}/demographics")
def demographics(sid: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = _own_submission(db, user, sid)
    m = _model_for(db, s.id)
    if not m:
        return []
    return db.query(DemographicImpact).filter(
        DemographicImpact.model_id == m.id
    ).order_by(DemographicImpact.id).all()


@router.get("/{sid}/stakeholders")
def stakeholders(sid: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = _own_submission(db, user, sid)
    m = _model_for(db, s.id)
    if not m:
        return []
    return db.query(StakeholderRecord).filter(
        StakeholderRecord.model_id == m.id
    ).order_by(StakeholderRecord.id).all()


@router.get("/{sid}/analogies")
def analogies(sid: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = _own_submission(db, user, sid)
    m = _model_for(db, s.id)
    if not m:
        return []
    return db.query(HistoricalAnalogy).filter(
        HistoricalAnalogy.model_id == m.id
    ).order_by(HistoricalAnalogy.id).all()


@router.delete("/{sid}")
def delete_submission(sid: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = _own_submission(db, user, sid)
    m = _model_for(db, s.id)
    if m:
        db.query(DemographicImpact).filter(DemographicImpact.model_id == m.id).delete(synchronize_session=False)
        db.query(HistoricalAnalogy).filter(HistoricalAnalogy.model_id == m.id).delete(synchronize_session=False)
        db.query(StakeholderRecord).filter(StakeholderRecord.model_id == m.id).delete(synchronize_session=False)
        for n in db.query(EffectNode).filter(EffectNode.model_id == m.id).order_by(EffectNode.id.desc()).all():
            db.delete(n)
        db.flush()
        db.query(ImpactModel).filter(ImpactModel.id == m.id).delete(synchronize_session=False)
    db.query(PolicySubmission).filter(PolicySubmission.id == s.id).delete(synchronize_session=False)
    db.commit()
    return {"ok": True}
