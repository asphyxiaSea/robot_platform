from app.workflows.voice_control.state import VoiceControlState


def finalize_node(state: VoiceControlState) -> VoiceControlState:
    trace = list(state.get("trace", []))
    trace.append("finalize")
    return {
        **state,
        "trace": trace,
    }
