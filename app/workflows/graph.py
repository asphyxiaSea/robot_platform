from langgraph.graph import END, StateGraph

from app.workflows.nodes import (
    fallback_node,
    finalize_node,
    preprocess_node,
    reminder_node,
    route_intent_node,
    weather_node,
)
from app.workflows.state import WorkflowState


def _pick_route(state: WorkflowState) -> str:
    return state.get("route", "fallback")


def build_workflow_graph():
    workflow = StateGraph(WorkflowState)

    workflow.add_node("preprocess", preprocess_node)
    workflow.add_node("route_intent", route_intent_node)
    workflow.add_node("weather", weather_node)
    workflow.add_node("reminder", reminder_node)
    workflow.add_node("fallback", fallback_node)
    workflow.add_node("finalize", finalize_node)

    workflow.set_entry_point("preprocess")
    workflow.add_edge("preprocess", "route_intent")

    workflow.add_conditional_edges(
        "route_intent",
        _pick_route,
        {
            "weather": "weather",
            "reminder": "reminder",
            "fallback": "fallback",
        },
    )

    workflow.add_edge("weather", "finalize")
    workflow.add_edge("reminder", "finalize")
    workflow.add_edge("fallback", "finalize")
    workflow.add_edge("finalize", END)

    return workflow.compile()


graph = build_workflow_graph()
