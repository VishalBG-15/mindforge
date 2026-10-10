from typing import Any, Dict
from app.agent.state import AgentState
from app.models.habit import Habit, HabitLog


def run_node_ingest(state: AgentState) -> Dict[str, Any]:
    """
    Node 1 (LangGraph Node): Ingestion Engine.
    Queries the database and extracts clean dictionaries so downstream
    agents do not have ORM session-detachment issues.
    """
    db = state["db"]
    habit_id = state["habit_id"]

    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        raise ValueError(f"Habit with ID {habit_id} does not exist.")

    # Pull the 14 most recent logs
    logs = (
        db.query(HabitLog)
        .filter(HabitLog.habit_id == habit_id)
        .order_by(HabitLog.logged_at.desc())
        .limit(14)
        .all()
    )

    clean_logs = [
        {
            "id": log.id,
            "completed": log.completed,
            "notes": log.notes or "",
            "logged_at": str(log.logged_at),
        }
        for log in logs
    ]

    return {
        "habit_title": habit.title,
        "habit_description": habit.description,
        "original_target": habit.target_count,
        "raw_logs": clean_logs,
        "final_adjusted_target": habit.target_count,
    }