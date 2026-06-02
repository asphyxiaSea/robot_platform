import json
from typing import Any

from app.core.llm import get_voice_control_llm
from app.workflows.voice_control.state import VoiceControlState


_SYSTEM_PROMPT = """你是机器人底盘控制意图解析器。
只输出 JSON，不要输出任何额外文本。
仅允许动作: forward, backward, turn_left, turn_right, stop。
如果无法识别有效移动指令，route 必须是 fallback。
输出 JSON 字段: route, intent, action, linear_x, angular_z, response。
速度约束: linear_x 在 [-0.5, 0.5]，angular_z 在 [-1.0, 1.0]。
"""


def _clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _extract_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        merged: list[str] = []
        for part in content:
            if isinstance(part, dict) and isinstance(part.get("text"), str):
                merged.append(part["text"])
            elif isinstance(part, str):
                merged.append(part)
        return "".join(merged)
    return ""


def llm_route_intent_node(state: VoiceControlState) -> VoiceControlState:
    trace = list(state.get("trace", []))
    trace.append("llm_route_intent")

    normalized_text = state.get("normalized_text", "")
    if not normalized_text:
        return {
            **state,
            "intent": "unknown",
            "route": "fallback",
            "error": state.get("error", "") or "llm: empty text",
            "trace": trace,
        }

    try:
        llm = get_voice_control_llm()
        user_prompt = f"用户指令: {normalized_text}"
        message = llm.invoke(
            [
                ("system", _SYSTEM_PROMPT),
                ("user", user_prompt),
            ]
        )

        raw = _extract_content(getattr(message, "content", ""))
        data = json.loads(raw)

        route = str(data.get("route", "fallback")).strip().lower()
        intent = str(data.get("intent", "unknown")).strip().lower()
        action = str(data.get("action", "stop")).strip().lower()

        if action not in {"forward", "backward", "turn_left", "turn_right", "stop"}:
            action = "stop"

        linear_x = _clamp(_to_float(data.get("linear_x", 0.0)), -0.5, 0.5)
        angular_z = _clamp(_to_float(data.get("angular_z", 0.0)), -1.0, 1.0)
        response = str(data.get("response", "")).strip()

        if route not in {"move", "fallback"}:
            route = "fallback"

        if route == "fallback":
            return {
                **state,
                "intent": intent,
                "route": "fallback",
                "action": action,
                "linear_x": linear_x,
                "angular_z": angular_z,
                "llm_raw": raw,
                "trace": trace,
            }

        if not response:
            action_to_response = {
                "forward": "收到，正在前进，1秒后自动停止。",
                "backward": "收到，正在后退，1秒后自动停止。",
                "turn_left": "收到，正在左转，1秒后自动停止。",
                "turn_right": "收到，正在右转，1秒后自动停止。",
                "stop": "收到，正在停止。",
            }
            response = action_to_response.get(action, "收到，正在停止。")

        return {
            **state,
            "intent": intent or "move",
            "route": "move",
            "action": action,
            "linear_x": linear_x,
            "angular_z": angular_z,
            "response": response,
            "llm_raw": raw,
            "error": "",
            "trace": trace,
        }
    except Exception as exc:
        return {
            **state,
            "intent": "unknown",
            "route": "fallback",
            "error": f"llm route failed: {exc}",
            "trace": trace,
        }
