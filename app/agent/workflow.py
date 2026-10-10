from functools import lru_cache
from typing import Any, Dict

from langgraph.graph import END, START, StateGraph
from sqlalchemy.orm import Session

from app.agent.node_1_ingest import run_node_ingest
from app.agent.node_2_analytics import run_node_analytics
from app.agent.node_3_friction import run_node_friction
from app.agent.node_4_critic import run_node_critic
from app.agent.node_4_strategy import run_node_strategy
from app.agent.node_5_synthesis import run_node_synthesis
from app.agent.node_6_persist import run_node_persist
from app.agent.state import AgentState


@lru_cache(maxsize=1)
def build_workflow():
    graph = StateGraph(AgentState)
    graph.add_node("ingest", run_node_ingest)
    graph.add_node("analytics", run_node_analytics)
    graph.add_node("diagnostic_profiler", run_node_friction)
    graph.add_node("strategy_architect", run_node_strategy)
    graph.add_node("feasibility_critic", run_node_critic)
    graph.add_node("coaching_communicator", run_node_synthesis)
    graph.add_node("persist", run_node_persist)

    graph.add_edge(START, "ingest")
    graph.add_edge("ingest", "analytics")
    graph.add_edge("analytics", "diagnostic_profiler")
    graph.add_edge("diagnostic_profiler", "strategy_architect")
    graph.add_edge("strategy_architect", "feasibility_critic")
    graph.add_edge("feasibility_critic", "coaching_communicator")
    graph.add_edge("coaching_communicator", "persist")
    graph.add_edge("persist", END)
    return graph.compile()


def run_council(db: Session, habit_id: int) -> Dict[str, Any]:
    final_state = build_workflow().invoke(
        {"db": db, "habit_id": habit_id, "deliberation": []}
    )
    return {
        "session_id": final_state["persisted_session_id"],
        "created_at": final_state["persisted_at"],
        "habit_id": final_state["habit_id"],
        "habit_title": final_state["habit_title"],
        "analytics": final_state["analytics"],
        "diagnosis": final_state["diagnosis"],
        "strategy": final_state["selected_strategy"],
        "strategy_rationale": final_state["strategy_rationale"],
        "proposed_target": final_state["proposed_target"],
        "audit_verdict": final_state["audit_verdict"],
        "critic_rationale": final_state["critic_rationale"],
        "final_adjusted_target": final_state["final_adjusted_target"],
        "coaching_mandate": final_state["coaching_mandate"],
        "coaching_message": final_state["coaching_message"],
        "deliberation": final_state["deliberation"],
    }
