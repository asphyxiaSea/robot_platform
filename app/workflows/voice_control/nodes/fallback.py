from app.workflows.voice_control.state import VoiceControlState


def fallback_node(state: VoiceControlState) -> VoiceControlState:
    trace = list(state.get("trace", []))
    trace.append("fallback")
    error = str(state.get("error", "") or "")
    if error.startswith("llm"):
        response = "抱歉，我暂时无法理解这条语音指令，请稍后再试。"
    else:
        response = "未识别到移动指令."

    return {
        **state,
        "response": response,
        "trace": trace,
    }
