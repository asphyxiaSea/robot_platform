import time

from app.workflows.voice_control.nodes.common import MOVE_DURATION_S, publish_cmd_vel
from app.workflows.voice_control.state import VoiceControlState


def move_robot_node(state: VoiceControlState) -> VoiceControlState:
    trace = list(state.get("trace", []))
    trace.append("move")

    action = str(state.get("action", "stop") or "stop")
    linear_x = float(state.get("linear_x", 0.0) or 0.0)
    angular_z = float(state.get("angular_z", 0.0) or 0.0)

    if action == "forward":
        response = state.get("response", "") or "收到，正在前进，1秒后自动停止。"
    elif action == "backward":
        response = state.get("response", "") or "收到，正在后退，1秒后自动停止。"
    elif action == "turn_left":
        response = state.get("response", "") or "收到，正在左转，1秒后自动停止。"
    elif action == "turn_right":
        response = state.get("response", "") or "收到，正在右转，1秒后自动停止。"
    else:
        action = "stop"
        linear_x = 0.0
        angular_z = 0.0
        response = state.get("response", "") or "收到，正在停止。"

    try:
        publish_cmd_vel(linear_x=linear_x, angular_z=angular_z)
        executed = True

        # Safety policy: every motion command is followed by an automatic stop.
        if action != "stop":
            time.sleep(MOVE_DURATION_S)
            publish_cmd_vel(linear_x=0.0, angular_z=0.0)

        error = ""
    except Exception as exc:
        executed = False
        error = str(exc)
        response = f"机器人控制失败：{exc}"

    return {
        **state,
        "action": action,
        "linear_x": linear_x,
        "angular_z": angular_z,
        "duration_s": MOVE_DURATION_S,
        "executed": executed,
        "safety_stop_applied": action != "stop" and executed,
        "error": error,
        "response": response,
        "trace": trace,
    }
