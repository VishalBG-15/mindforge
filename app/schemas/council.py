from typing import Literal, List

from pydantic import BaseModel, Field


class CouncilAnalytics(BaseModel):
    total_logs: int
    completion_rate: float
    current_streak: int
    consecutive_misses: int


class CouncilDiagnosis(BaseModel):
    friction: Literal[
        "HIGH_RESISTANCE_BURNOUT",
        "STREAK_BREAK_DANGER",
        "FORGETFULNESS_NO_ROUTINE",
        "LOW_FRICTION_STABLE",
    ]
    surface_excuse: str
    actual_mechanism: str
    reasoning: str


class CouncilStrategy(BaseModel):
    id: str
    book: str
    author: str
    rule_name: str
    friction_trigger: str
    downscale_factor: float
    core_principle: str
    coaching_directive: str


class CouncilDeliberation(BaseModel):
    agent: str
    finding: str
    reasoning: str


class CouncilResponse(BaseModel):
    session_id: int
    created_at: str
    habit_id: int
    habit_title: str
    analytics: CouncilAnalytics
    diagnosis: CouncilDiagnosis
    strategy: CouncilStrategy
    strategy_rationale: str
    proposed_target: int = Field(ge=1)
    audit_verdict: Literal["APPROVE", "REVISE"]
    critic_rationale: str
    final_adjusted_target: int = Field(ge=1)
    coaching_mandate: str
    coaching_message: str
    deliberation: List[CouncilDeliberation]
