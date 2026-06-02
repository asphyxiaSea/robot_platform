from langgraph.graph import END, StateGraph

from app.workflows.voice_control.nodes import (
    fallback_node,
    finalize_node,
    llm_route_intent_node,
    move_robot_node,
    preprocess_node,
    transcribe_node,
)
from app.workflows.voice_control.state import VoiceControlState


def _pick_route(state: VoiceControlState) -> str:
    return state.get("route", "fallback")


def build_voice_control_graph():
    workflow = StateGraph(VoiceControlState)

    workflow.add_node("transcribe", transcribe_node)
    workflow.add_node("preprocess", preprocess_node)
    workflow.add_node("llm_route_intent", llm_route_intent_node)
    workflow.add_node("move", move_robot_node)
    workflow.add_node("fallback", fallback_node)
    workflow.add_node("finalize", finalize_node)

    workflow.set_entry_point("transcribe")
    workflow.add_edge("transcribe", "preprocess")
    workflow.add_edge("preprocess", "llm_route_intent")

    workflow.add_conditional_edges(
        "llm_route_intent",
        _pick_route,
        {
            "move": "move",
            "fallback": "fallback",
        },
    )

    workflow.add_edge("move", "finalize")
    workflow.add_edge("fallback", "finalize")
    workflow.add_edge("finalize", END)

    return workflow.compile()


voice_control_graph = build_voice_control_graph()
