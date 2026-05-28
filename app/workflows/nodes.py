from app.workflows.state import WorkflowState


def preprocess_node(state: WorkflowState) -> WorkflowState:
    text = state.get("text", "")
    normalized = " ".join(text.strip().lower().split())
    trace = list(state.get("trace", []))
    trace.append("preprocess")
    return {
        **state,
        "normalized_text": normalized,
        "trace": trace,
    }


def route_intent_node(state: WorkflowState) -> WorkflowState:
    text = state.get("normalized_text", "")
    trace = list(state.get("trace", []))
    trace.append("route_intent")

    if any(word in text for word in ["天气", "weather", "温度"]):
        intent = "weather"
        route = "weather"
    elif any(word in text for word in ["提醒", "remind", "待办"]):
        intent = "reminder"
        route = "reminder"
    else:
        intent = "unknown"
        route = "fallback"

    return {
        **state,
        "intent": intent,
        "route": route,
        "trace": trace,
    }


def weather_node(state: WorkflowState) -> WorkflowState:
    trace = list(state.get("trace", []))
    trace.append("weather")
    return {
        **state,
        "response": "这是天气模板分支：你可以在这里接入真实天气服务。",
        "trace": trace,
    }


def reminder_node(state: WorkflowState) -> WorkflowState:
    trace = list(state.get("trace", []))
    trace.append("reminder")
    return {
        **state,
        "response": "这是提醒模板分支：你可以在这里接入任务管理逻辑。",
        "trace": trace,
    }


def fallback_node(state: WorkflowState) -> WorkflowState:
    trace = list(state.get("trace", []))
    trace.append("fallback")
    return {
        **state,
        "response": "未识别到已支持的意图，请尝试天气或提醒相关指令。",
        "trace": trace,
    }


def finalize_node(state: WorkflowState) -> WorkflowState:
    trace = list(state.get("trace", []))
    trace.append("finalize")
    return {
        **state,
        "trace": trace,
    }
