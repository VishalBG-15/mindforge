import operator
from typing import Annotated, Any, Dict, List, Optional

from sqlalchemy.orm import Session
from typing_extensions import TypedDict


class AgentState(TypedDict, total=False):
    db: Session
    habit_id: int
    habit_title: str
    habit_description: Optional[str]
    original_target: int
    raw_logs: List[Dict[str, Any]]
    analytics: Dict[str, Any]
    diagnosis: Dict[str, Any]
    selected_strategy: Dict[str, Any]
    strategy_rationale: str
    proposed_target: int
    audit_verdict: str
    critic_rationale: str
    final_adjusted_target: int
    coaching_mandate: str
    coaching_message: str
    deliberation: Annotated[List[Dict[str, str]], operator.add]
    persisted_session_id: int
    persisted_at: Optional[str]
