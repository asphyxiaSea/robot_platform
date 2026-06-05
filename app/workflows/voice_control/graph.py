from langgraph.graph import END, StateGraph
from langgraph.types import Command

from app.workflows.voice_control.nodes import (
    transcribe_node,
    tts_node,
)
from app.workflows.voice_control.nodes.llm_node import llm_node
from app.workflows.voice_control.nodes.tool_node import robot_tool_node
from app.workflows.voice_control.state import VoiceControlState


def build_voice_control_graph():
    workflow = StateGraph(VoiceControlState)

    workflow.add_node("transcribe", transcribe_node)
    workflow.add_node("llm", llm_node)
    workflow.add_node("tools", robot_tool_node)
    workflow.add_node("tts", tts_node)

    workflow.set_entry_point("transcribe")
    workflow.add_edge("transcribe", "llm")
    workflow.add_edge("tools", "tts")
    workflow.add_edge("tts", END)

    return workflow.compile()


voice_control_graph = build_voice_control_graph()