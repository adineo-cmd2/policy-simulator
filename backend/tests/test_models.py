from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models.demographic_impact import DemographicImpact
from app.models.effect_node import EffectNode
from app.models.historical_analogy import HistoricalAnalogy
from app.models.impact_model import ImpactModel
from app.models.policy_submission import PolicySubmission
from app.models.stakeholder_record import StakeholderRecord
from app.models.user import User


def test_submission_model_effect_rows_link():
    for table in (StakeholderRecord.__table__, HistoricalAnalogy.__table__,
                  DemographicImpact.__table__, EffectNode.__table__,
                  ImpactModel.__table__, PolicySubmission.__table__,
                  User.__table__):
        table.drop(bind=engine, checkfirst=True)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    u = User(email="t9@example.com", password_hash=hash_password("secret123"))
    db.add(u)
    db.commit()
    db.refresh(u)
    s = PolicySubmission(
        user_id=u.id,
        policy_text="Cap annual rent increases at 3% in urban areas.",
        jurisdiction="Test City",
        policy_domain="housing",
        context="rental market",
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    assert s.policy_domain == "housing"
    m = ImpactModel(submission_id=s.id)
    db.add(m)
    db.commit()
    db.refresh(m)
    assert m.submission_id == s.id
    parent = EffectNode(
        model_id=m.id,
        parent_id=None,
        order=1,
        title="Rental supply adjusts",
        detail="Speculative modelling: landlords adjust supply.",
        domain_area="housing",
        magnitude="medium",
        direction="mixed",
        confidence="medium",
        analogy="Rent stabilization precedent",
    )
    db.add(parent)
    db.commit()
    db.refresh(parent)
    child = EffectNode(
        model_id=m.id,
        parent_id=parent.id,
        order=2,
        title="Maintenance response",
        detail="Speculative modelling: maintenance spending responds.",
        domain_area="housing",
        magnitude="low",
        direction="negative",
        confidence="speculative",
        analogy="",
    )
    db.add(child)
    db.commit()
    db.refresh(child)
    assert child.parent_id == parent.id
    d = DemographicImpact(
        model_id=m.id,
        effect_id=parent.id,
        group_name="low-income",
        impact_type="benefit",
        magnitude="medium",
        explanation="Speculative modelling: near-term cost relief.",
    )
    a = HistoricalAnalogy(
        model_id=m.id,
        effect_id=parent.id,
        title="Rent Stabilization Act",
        jurisdiction="Test City",
        year=2019,
        outcome="Speculative modelling: mixed supply effects.",
        similarity="medium",
    )
    st = StakeholderRecord(
        model_id=m.id,
        group_name="renters",
        stance="benefit",
        rating=4,
        explanation="Speculative modelling: lower increases.",
    )
    db.add_all([d, a, st])
    db.commit()
    assert db.query(EffectNode).filter_by(model_id=m.id).count() == 2
    assert db.query(DemographicImpact).filter_by(model_id=m.id).count() == 1
    assert db.query(HistoricalAnalogy).filter_by(model_id=m.id).count() == 1
    assert db.query(StakeholderRecord).filter_by(model_id=m.id).count() == 1
    assert d.effect_id == parent.id
    assert a.effect_id == parent.id
    db.close()
