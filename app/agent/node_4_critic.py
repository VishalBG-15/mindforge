from typing import Any, Dict, Literal

from pydantic import BaseModel, Field

from app.agent.llm import AgentResponseError, request_structured_response
from app.agent.state import AgentState


class FeasibilityReview(BaseModel):
    verdict: Literal["APPROVE", "REVISE"]
    adjusted_target: int = Field(ge=1)
    rationale: str = Field(max_length=700)
    coaching_mandate: str = Field(min_length=1, max_length=700)


def run_node_critic(state: AgentState) -> Dict[str, Any]:
    original_target = state["original_target"]
    review = request_structured_response(
        (
            "You are Agent 3, the Feasibility Critic. Independently review the proposed "
            "habit adjustment for realism, safety, and alignment with the evidence. "
            "Approve or revise it. The adjusted target must be between 1 and the "
            "original target inclusive. Return JSON with verdict (APPROVE or REVISE), "
            "adjusted_target, rationale, and coaching_mandate."
        ),
        (
            f"Habit: {state['habit_title']}\n"
            f"Original target: {original_target}\n"
            f"Analytics: {state['analytics']}\n"
            f"Diagnostic assessment: {state['diagnosis']}\n"
            f"Selected strategy: {state['selected_strategy']}\n"
            f"Strategy rationale: {state['strategy_rationale']}\n"
            f"Proposed target: {state['proposed_target']}"
        ),
        FeasibilityReview,
    )
    if review.adjusted_target > original_target:
        raise AgentResponseError(
            "The feasibility critic proposed a target above the habit's current target."
        )

    return {
        "audit_verdict": review.verdict,
        "final_adjusted_target": review.adjusted_target,
        "critic_rationale": review.rationale,
        "coaching_mandate": review.coaching_mandate,
        "deliberation": [
            {
                "agent": "Feasibility Critic",
                "finding": f"{review.verdict.title()} the {review.adjusted_target}-unit target.",
                "reasoning": review.rationale,
            }
        ],
    }
