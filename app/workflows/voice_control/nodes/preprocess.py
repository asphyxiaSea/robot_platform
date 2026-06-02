from app.workflows.voice_control.state import VoiceControlState


def preprocess_node(state: VoiceControlState) -> VoiceControlState:
    text = state.get("text", "")
    normalized = " ".join(text.strip().lower().split())
    trace = list(state.get("trace", []))
    trace.append("preprocess")
    return {
        **state,
        "normalized_text": normalized,
        "trace": trace,
    }
