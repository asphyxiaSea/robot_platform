from app.workflows.voice_control.state import VoiceControlState


def route_intent_node(state: VoiceControlState) -> VoiceControlState:
    text = state.get("normalized_text", "")
    trace = list(state.get("trace", []))
    trace.append("route_intent")

    if any(word in text for word in ["前进", "后退", "左转", "右转", "停止"]):
        intent = "move"
        route = "move"
    else:
        intent = "unknown"
        route = "fallback"

    return {
        **state,
        "intent": intent,
        "route": route,
        "trace": trace,
    }
