from typing import Any, Dict

from pydantic import BaseModel, Field

from app.agent.llm import request_structured_response
from app.agent.state import AgentState


class CoachingSynthesis(BaseModel):
    coaching_message: str = Field(min_length=1, max_length=1200)


def run_node_synthesis(state: AgentState) -> Dict[str, Any]:
    synthesis = request_structured_response(
        (
            "You are Agent 4, the Coaching Communicator. Turn the council's evidence "
            "and approved mandate into a brief, warm, specific, non-judgmental coaching "
            "message. Do not add unsupported claims or shame the user. Return JSON with "
            "one field, coaching_message."
        ),
        (
            f"Habit: {state['habit_title']}\n"
            f"Analytics: {state['analytics']}\n"
            f"Diagnosis: {state['diagnosis']}\n"
            f"Selected strategy: {state['selected_strategy']}\n"
            f"Critic verdict: {state['audit_verdict']}\n"
            f"Final target: {state['final_adjusted_target']} (original "
            f"{state['original_target']})\n"
            f"Critic rationale: {state['critic_rationale']}\n"
            f"Coaching mandate: {state['coaching_mandate']}"
        ),
        CoachingSynthesis,
    )
    return {
        "coaching_message": synthesis.coaching_message,
        "deliberation": [
            {
                "agent": "Coaching Communicator",
                "finding": synthesis.coaching_message,
                "reasoning": state["coaching_mandate"],
            }
        ],
    }
