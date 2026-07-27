from langchain_core.tools import tool
from app.core.docker_ros2 import DockerROS2
import websocket
from app.core.config import settings
import json

@tool
def start_explore() -> str:
    """启动自动探索，机器人开始自主移动建图，必须在封闭区域内使用"""
    DockerROS2.run_bg("ros2 launch explore_lite explore.launch.py use_sim_time:=false")
    return "自动探索已启动，完成后说保存地图"



@tool
def stop_explore() -> str:
    """停止自动探索"""
    ws = websocket.WebSocket()
    ws.connect(settings.robot_ws_url, timeout=5)
    try:
        ws.send(json.dumps({
            "op": "publish",
            "topic": "explore/resume",
            "msg": {"data": False}
        }))
    finally:
        ws.close()
    return "自动探索已停止"


@tool
def resume_explore() -> str:
    """恢复自动探索"""
    ws = websocket.WebSocket()
    ws.connect(settings.robot_ws_url, timeout=5)
    try:
        ws.send(json.dumps({
            "op": "publish",
            "topic": "explore/resume",
            "msg": {"data": True}
        }))
    finally:
        ws.close()
    return "自动探索已恢复"


@tool
def save_map() -> str:
    """保存当前建好的地图"""
    ws = websocket.WebSocket()
    ws.connect(settings.robot_ws_url, timeout=5)
    try:
        ws.send(json.dumps({
            "op": "call_service",
            "service": "/slam_toolbox/save_map",
            "type": "slam_toolbox/srv/SaveMap",
            "args": {
                "name": {
                    "data": "/home/ws/ugv_ws/src/ugv_main/ugv_nav/maps/map"
                }
            }
        }))
        result = json.loads(ws.recv())
        if result.get("result"):
            return "地图保存成功"
        return f"地图保存失败: {result}"
    finally:
        ws.close()


mapping_tools = [
    start_explore, resume_explore, stop_explore, save_map,
]