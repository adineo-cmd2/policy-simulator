from typing import Optional

from pydantic import BaseModel, Field


class PolicySubmitIn(BaseModel):
    policy_text: str
    jurisdiction: str = ""
    policy_domain: str = "general"
    context: str = ""
    target_demographic: str = ""


class EffectOut(BaseModel):
    id: int
    model_id: int
    parent_id: Optional[int] = None
    order: int
    title: str
    detail: str
    domain_area: str
    magnitude: str
    direction: str
    confidence: str
    analogy: str = ""

    class Config:
        from_attributes = True


class DemographicOut(BaseModel):
    id: int
    model_id: int
    effect_id: int
    group_name: str
    impact_type: str
    magnitude: str
    explanation: str

    class Config:
        from_attributes = True


class AnalogyOut(BaseModel):
    id: int
    model_id: int
    effect_id: int
    title: str
    jurisdiction: str
    year: int
    outcome: str
    similarity: str

    class Config:
        from_attributes = True


class StakeholderOut(BaseModel):
    id: int
    model_id: int
    group_name: str
    stance: str
    rating: int
    explanation: str

    class Config:
        from_attributes = True


class PolicySubmitOut(BaseModel):
    submission_id: int
    model_id: int = 0
    effects: list = Field(default_factory=list)
