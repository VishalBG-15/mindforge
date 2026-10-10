from typing import Any, Dict

from app.agent.state import AgentState


def run_node_analytics(state: AgentState) -> Dict[str, Any]:
    logs = state["raw_logs"]

    if not logs:
        return {
            "analytics": {
                "total_logs": 0,
                "completion_rate": 0.0,
                "current_streak": 0,
                "consecutive_misses": 0,
            }
        }

    # Rolling window of the 7 most recent entries
    window = logs[:7]
    completed_count = sum(1 for log in window if log["completed"])
    completion_rate = round(completed_count / len(window), 4)

    # Current consecutive completion streak (newest backwards)
    current_streak = 0
    for log in logs:
        if log["completed"]:
            current_streak += 1
        else:
            break

    # Consecutive missed check-ins
    consecutive_misses = 0
    for log in logs:
        if not log["completed"]:
            consecutive_misses += 1
        else:
            break

    return {
        "analytics": {
            "total_logs": len(logs),
            "completion_rate": completion_rate,
            "current_streak": current_streak,
            "consecutive_misses": consecutive_misses,
        }
    }