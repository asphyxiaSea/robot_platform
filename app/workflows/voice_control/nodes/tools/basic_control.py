import json
import math
import time

import websocket
from langchain_core.tools import tool

from app.core.config import settings


def _publish_cmd_vel(linear_x: float, angular_z: float) -> None:
    ws = websocket.WebSocket()
    ws.connect(settings.robot_ws_url, timeout=2)
    try:
        ws.send(json.dumps({
            "op": "publish",
            "topic": "/cmd_vel",
            "msg": {
                "linear": {"x": linear_x, "y": 0.0, "z": 0.0},
                "angular": {"x": 0.0, "y": 0.0, "z": angular_z},
            },
        }))
    finally:
        ws.close()


def _publish_led(io4: float, io5: float) -> None:
    ws = websocket.WebSocket()
    ws.connect(settings.robot_ws_url, timeout=2)
    try:
        ws.send(json.dumps({
            "op": "publish",
            "topic": "/ugv/led_ctrl",
            "msg": {
                "layout": {"dim": [], "data_offset": 0},
                "data": [io4, io5],
            },
        }))
    finally:
        ws.close()


def _publish_gimbal(pan_degree: float, tilt_degree: float) -> None:
    ws = websocket.WebSocket()
    ws.connect(settings.robot_ws_url, timeout=2)
    try:
        ws.send(json.dumps({
            "op": "publish",
            "topic": "/ugv/joint_states",
            "msg": {
                "header": {"stamp": {"sec": 0, "nanosec": 0}, "frame_id": ""},
                "name": [
                    "left_up_wheel_link_joint",
                    "left_down_wheel_link_joint",
                    "right_up_wheel_link_joint",
                    "right_down_wheel_link_joint",
                    "pt_base_link_to_pt_link1",
                    "pt_link1_to_pt_link2",
                ],
                "position": [0.0, 0.0, 0.0, 0.0,
                             math.radians(pan_degree),
                             math.radians(tilt_degree)],
                "velocity": [],
                "effort": [],
            },
        }))
    finally:
        ws.close()


def _move(linear_x: float, angular_z: float, duration: float) -> None:
    _publish_cmd_vel(linear_x, angular_z)
    time.sleep(duration)
    _publish_cmd_vel(0.0, 0.0)


@tool
def drive_on_heading(units: float) -> str:
    """让机器人向前移动，units 为持续时间（秒）"""
    _move(0.5, 0.0, units)
    return f"前进 {units} 秒"


@tool
def back_up(units: float) -> str:
    """让机器人向后移动，units 为持续时间（秒）"""
    _move(-0.5, 0.0, units)
    return f"后退 {units} 秒"


@tool
def spin(degrees: float) -> str:
    """让机器人旋转，正数左转，负数右转，degrees 为角度"""
    duration = abs(degrees) / 90.0
    angular_z = 1.0 if degrees > 0 else -1.0
    _move(0.0, angular_z, duration)
    return f"旋转 {degrees} 度"


@tool
def stop() -> str:
    """让机器人立即停止"""
    _publish_cmd_vel(0.0, 0.0)
    return "已停止"


@tool
def led_on() -> str:
    """打开机器人所有灯光"""
    _publish_led(1.0, 1.0)
    return "灯光已全部打开"


@tool
def led_off() -> str:
    """关闭机器人所有灯光"""
    _publish_led(0.0, 0.0)
    return "灯光已全部关闭"


@tool
def led_ctrl(io4: float, io5: float) -> str:
    """单独控制机器人灯光，io4 和 io5 各自为 0.0（关）或 1.0（开）"""
    _publish_led(io4, io5)
    return f"灯光控制: IO4={'开' if io4 else '关'}, IO5={'开' if io5 else '关'}"


@tool
def set_gimbal(pan_degree: float, tilt_degree: float) -> str:
    """
    控制云台转动。
    pan_degree: 水平角度，正数左转，负数右转，范围约 -90 ~ 90。
    tilt_degree: 俯仰角度，正数抬头，负数低头，范围约 -90 ~ 90。
    """
    _publish_gimbal(pan_degree, tilt_degree)
    return f"云台 -> 水平: {pan_degree}°, 俯仰: {tilt_degree}°"


@tool
def reset_gimbal() -> str:
    """将云台归位到正前方水平位置"""
    _publish_gimbal(0.0, 0.0)
    return "云台已归位"


basic_control_tools = [
    drive_on_heading, back_up, spin, stop,
    led_on, led_off, led_ctrl,
    set_gimbal, reset_gimbal,
]