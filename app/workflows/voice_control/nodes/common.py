import json

import websocket


ROBOT_WS_URL = "ws://127.0.0.1:9090"
MOVE_DURATION_S = 1.0


def publish_cmd_vel(linear_x: float, angular_z: float) -> None:
    ws = websocket.WebSocket()
    ws.connect(ROBOT_WS_URL, timeout=2)
    try:
        cmd = {
            "op": "publish",
            "topic": "/cmd_vel",
            "msg": {
                "linear": {"x": linear_x, "y": 0.0, "z": 0.0},
                "angular": {"x": 0.0, "y": 0.0, "z": angular_z},
            },
        }
        ws.send(json.dumps(cmd))
    finally:
        ws.close()
