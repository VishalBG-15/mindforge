from datetime import datetime
from typing import Any, Dict

from app.agent.state import AgentState
from app.models.habit import CouncilSession


def run_node_persist(state: AgentState) -> Dict[str, Any]:
    result = {
        "habit_id": state["habit_id"],
        "habit_title": state["habit_title"],
        "analytics": state["analytics"],
        "diagnosis": state["diagnosis"],
        "strategy": state["selected_strategy"],
        "strategy_rationale": state["strategy_rationale"],
        "proposed_target": state["proposed_target"],
        "audit_verdict": state["audit_verdict"],
        "critic_rationale": state["critic_rationale"],
        "final_adjusted_target": state["final_adjusted_target"],
        "coaching_mandate": state["coaching_mandate"],
        "coaching_message": state["coaching_message"],
        "deliberation": state["deliberation"],
    }
    session = CouncilSession(habit_id=state["habit_id"], result=result)
    db = state["db"]
    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "persisted_session_id": session.id,
        "persisted_at": (
            session.created_at.isoformat()
            if isinstance(session.created_at, datetime)
            else str(session.created_at)
        ),
    }
