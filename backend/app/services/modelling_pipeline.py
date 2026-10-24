"""Persist submission -> model -> effect tree -> linked rows."""

from app.models.demographic_impact import DemographicImpact
from app.models.effect_node import EffectNode
from app.models.historical_analogy import HistoricalAnalogy
from app.models.impact_model import ImpactModel
from app.models.policy_submission import PolicySubmission
from app.services import analogy_finder, demographic_analyser, impact_modeller
from app.services import stakeholder_mapper


def run_model(db, user_id: int, policy_text: str, jurisdiction: str,
              domain: str, context: str = "") -> dict:
    key = (domain or "").lower().strip() or "general"
    if key not in impact_modeller.DOMAIN_PACKS:
        key = "general"
    sub = PolicySubmission(
        user_id=user_id,
        policy_text=policy_text or "",
        jurisdiction=jurisdiction or "",
        policy_domain=key,
        context=context or "",
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    model = ImpactModel(submission_id=sub.id)
    db.add(model)
    db.commit()
    db.refresh(model)

    nodes = impact_modeller.model(policy_text or "", jurisdiction or "", key)
    idx_to_id: dict = {}
    for i, n in enumerate(nodes):
        parent_id = idx_to_id.get(n["parent_idx"]) if n["parent_idx"] is not None else None
        row = EffectNode(
            model_id=model.id,
            parent_id=parent_id,
            order=n["order"],
            title=n["title"],
            detail=n["detail"],
            domain_area=n["domain_area"],
            magnitude=n["magnitude"],
            direction=n["direction"],
            confidence=n["confidence"],
            analogy=n.get("analogy", ""),
        )
        db.add(row)
        db.flush()
        idx_to_id[i] = row.id
    db.commit()

    firsts = [n for n in nodes if n["order"] == 1]
    first_db_ids = [
        idx_to_id[i] for i, n in enumerate(nodes) if n["order"] == 1
    ]
    for node, effect_id in zip(firsts, first_db_ids):
        for d in demographic_analyser.rows([node]):
            db.add(DemographicImpact(
                model_id=model.id,
                effect_id=effect_id,
                group_name=d["group_name"],
                impact_type=d["impact_type"],
                magnitude=d["magnitude"],
                explanation=d["explanation"],
            ))
        a = analogy_finder.find(key, node.get("domain_area", ""))
        db.add(HistoricalAnalogy(
            model_id=model.id,
            effect_id=effect_id,
            title=a["title"],
            jurisdiction=a["jurisdiction"],
            year=a["year"],
            outcome=a["outcome"],
            similarity=a["similarity"],
        ))
    for s in stakeholder_mapper.map(firsts):
        from app.models.stakeholder_record import StakeholderRecord
        db.add(StakeholderRecord(
            model_id=model.id,
            group_name=s["group_name"],
            stance=s["stance"],
            rating=s["rating"],
            explanation=s["explanation"],
        ))
    db.commit()

    effects = [
        {
            "id": idx_to_id[i],
            "model_id": model.id,
            "parent_id": idx_to_id.get(n["parent_idx"]) if n["parent_idx"] is not None else None,
            "order": n["order"],
            "title": n["title"],
            "detail": n["detail"],
            "domain_area": n["domain_area"],
            "magnitude": n["magnitude"],
            "direction": n["direction"],
            "confidence": n["confidence"],
            "analogy": n.get("analogy", ""),
        }
        for i, n in enumerate(nodes)
    ]
    return {"submission_id": sub.id, "model_id": model.id, "effects": effects}
