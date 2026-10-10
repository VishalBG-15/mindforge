from typing import Any, Dict, Literal

from pydantic import BaseModel, Field

from app.agent.llm import request_structured_response
from app.agent.state import AgentState


FrictionType = Literal[
    "HIGH_RESISTANCE_BURNOUT",
    "STREAK_BREAK_DANGER",
    "FORGETFULNESS_NO_ROUTINE",
    "LOW_FRICTION_STABLE",
]


class FrictionAssessment(BaseModel):
    friction: FrictionType
    surface_excuse: str = Field(max_length=300)
    actual_mechanism: str = Field(max_length=500)
    reasoning: str = Field(max_length=700)


def run_node_friction(state: AgentState) -> Dict[str, Any]:
    evidence = {
        "habit": state["habit_title"],
        "description": state.get("habit_description"),
        "analytics": state["analytics"],
        "recent_reflections": [
            log["notes"] for log in state["raw_logs"] if log.get("notes")
        ][:7],
    }
    assessment = request_structured_response(
        (
            "You are Agent 1, the Diagnostic Profiler in a habit-coaching council. "
            "Use only the supplied evidence; do not diagnose medical conditions. "
            "Choose the best friction label from HIGH_RESISTANCE_BURNOUT, "
            "STREAK_BREAK_DANGER, FORGETFULNESS_NO_ROUTINE, or LOW_FRICTION_STABLE. "
            "Return JSON with friction, surface_excuse, actual_mechanism, and reasoning."
        ),
        f"Assess the habit friction from this evidence:\n{evidence}",
        FrictionAssessment,
    )
    diagnosis = assessment.model_dump()
    return {
        "diagnosis": diagnosis,
        "deliberation": [
            {
                "agent": "Diagnostic Profiler",
                "finding": assessment.actual_mechanism,
                "reasoning": assessment.reasoning,
            }
        ],
    }
