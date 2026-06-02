import websocket, json
import time

ws = websocket.WebSocket()
ws.connect("ws://192.168.1.179:9090")

# 控制机器人前进
cmd = {
    "op": "publish",
    "topic": "/cmd_vel",
    "msg": {
        "linear": {"x": 0.5, "y": 0.0, "z": 0.0},
        "angular": {"x": 0.0, "y": 0.0, "z": 0.0}
    }
}
ws.send(json.dumps(cmd))

time.sleep(0.5)  # 前进2秒

import websocket
import json

ws = websocket.WebSocket()
ws.connect("ws://192.168.1.179:9090")

cmd = {
    "op": "publish",
    "topic": "/cmd_vel",
    "msg": {
        "linear": {"x": 0.0, "y": 0.0, "z": 0.0},
        "angular": {"x": 0.0, "y": 0.0, "z": 0.0}
    }
}
ws.send(json.dumps(cmd))
ws.close()


# import websocket
# import json
# import time

# ws = websocket.WebSocket()
# ws.connect("ws://127.0.0.1:9090")

# def led_ctrl(io4: float, io5: float):
#     """
#     io4, io5: 0.0 = 关，1.0 = 开
#     """
#     cmd = {
#         "op": "publish",
#         "topic": "/ugv/led_ctrl",
#         "msg": {
#             "layout": {
#                 "dim": [],
#                 "data_offset": 0
#             },
#             "data": [io4, io5]
#         }
#     }
#     ws.send(json.dumps(cmd))

# # 全开
# led_ctrl(1.0, 1.0)
# time.sleep(2)
# # 只开 IO4
# led_ctrl(1.0, 0.0)
# time.sleep(2)
# # 只开 IO5
# led_ctrl(0.0, 1.0)
# time.sleep(2)
# # 全关
# led_ctrl(0.0, 0.0)

# ws.close()


# import websocket
# import json
# import math
# import time
# ws = websocket.WebSocket()
# ws.connect("ws://127.0.0.1:9090")

# def set_gimbal(pan_degree: float, tilt_degree: float):
#     """
#     控制云台转动
#     pan_degree:  水平角度，正数左转，负数右转，范围约 -90 ~ 90
#     tilt_degree: 俯仰角度，正数抬头，负数低头，范围约 -90 ~ 90
#     """
#     pan_rad = math.radians(pan_degree)
#     tilt_rad = math.radians(tilt_degree)

#     cmd = {
#         "op": "publish",
#         "topic": "/ugv/joint_states",
#         "msg": {
#             "header": {
#                 "stamp": {"sec": 0, "nanosec": 0},
#                 "frame_id": ""
#             },
#             "name": [
#                 "left_up_wheel_link_joint",
#                 "left_down_wheel_link_joint",
#                 "right_up_wheel_link_joint",
#                 "right_down_wheel_link_joint",
#                 "pt_base_link_to_pt_link1",
#                 "pt_link1_to_pt_link2"
#             ],
#             "position": [0.0, 0.0, 0.0, 0.0, pan_rad, tilt_rad],
#             "velocity": [],
#             "effort": []
#         }
#     }
#     ws.send(json.dumps(cmd))
#     print(f"云台 -> 水平: {pan_degree}°, 俯仰: {tilt_degree}°")

# # 测试
# set_gimbal(0, 0)      # 回中
# time.sleep(2)
# set_gimbal(45, 0)     # 左转 45 度
# time.sleep(2)
# set_gimbal(-45, 0)    # 右转 45 度
# time.sleep(2)
# set_gimbal(0, 30)     # 抬头 30 度
# time.sleep(2)
# set_gimbal(0, -30)    # 低头 30 度
# time.sleep(2)
# set_gimbal(0, 0)      # 回中

# ws.close()


