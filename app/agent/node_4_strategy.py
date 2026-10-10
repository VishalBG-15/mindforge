import json
from pathlib import Path
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from app.agent.llm import AgentResponseError, request_structured_response
from app.agent.state import AgentState


class StrategyRecommendation(BaseModel):
    strategy_id: str
    rationale: str = Field(max_length=700)
    proposed_target: int = Field(ge=1)


def _load_strategies() -> List[Dict[str, Any]]:
    strategies_path = Path(__file__).with_name("strategies.json")
    with strategies_path.open(encoding="utf-8") as strategies_file:
        strategies = json.load(strategies_file)
    if not isinstance(strategies, list) or not strategies:
        raise ValueError(f"No strategies were configured in {strategies_path}.")
    return strategies


def run_node_strategy(state: AgentState) -> Dict[str, Any]:
    strategies = _load_strategies()
    original_target = state["original_target"]
    recommendation = request_structured_response(
        (
            "You are Agent 2, the Strategy Architect in a habit-coaching council. "
            "Choose exactly one supplied strategy and recommend a practical target "
            "between 1 and the original target inclusive. Do not increase the target. "
            "Return JSON with strategy_id, rationale, and proposed_target."
        ),
        (
            f"Habit: {state['habit_title']}\n"
            f"Original target: {original_target}\n"
            f"Diagnosis: {state['diagnosis']}\n"
            f"Analytics: {state['analytics']}\n"
            f"Available strategies: {json.dumps(strategies, ensure_ascii=False)}"
        ),
        StrategyRecommendation,
    )

    selected = next(
        (strategy for strategy in strategies if strategy["id"] == recommendation.strategy_id),
        None,
    )
    if selected is None:
        raise AgentResponseError(
            f"The strategy agent selected unknown strategy '{recommendation.strategy_id}'."
        )
    if recommendation.proposed_target > original_target:
        raise AgentResponseError(
            "The strategy agent proposed a target above the habit's current target."
        )

    return {
        "selected_strategy": selected,
        "strategy_rationale": recommendation.rationale,
        "proposed_target": recommendation.proposed_target,
        "deliberation": [
            {
                "agent": "Strategy Architect",
                "finding": f"Recommended {selected['rule_name']}.",
                "reasoning": recommendation.rationale,
            }
        ],
    }
