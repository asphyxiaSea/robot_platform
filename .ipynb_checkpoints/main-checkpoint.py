from contextlib import AsyncExitStack, asynccontextmanager

from fastapi import FastAPI

from app.api.v1.workflow import router as workflow_router
from app.core.config import settings

import subprocess
import asyncio
import websocket


def is_rosbridge_running() -> bool:
    """检测 rosbridge 是否已经在运行"""
    try:
        ws = websocket.WebSocket()
        ws.connect("ws://127.0.0.1:9090", timeout=2)
        ws.close()
        return True
    except Exception:
        return False


def is_bringup_running() -> bool:
    """检测底盘驱动是否已经在运行"""
    result = subprocess.run(
        ['docker', 'exec', 'ugv_jetson_ros_humble', 'bash', '-c',
         'source /opt/ros/humble/setup.bash && '
         'source ~/ugv_ws/install/setup.bash && '
         'ros2 node list'],
        capture_output=True, text=True
    )
    return '/ugv_bringup' in result.stdout or 'ugv' in result.stdout


@asynccontextmanager
async def ros2_drivers(app: FastAPI):
    bringup_proc = None
    rosbridge_proc = None

    if not is_bringup_running():
        print("[启动] 启动底盘驱动...")
        bringup_proc = subprocess.Popen([
            'docker', 'exec', 'ugv_jetson_ros_humble', 'bash', '-c',
            'source /opt/ros/humble/setup.bash && '
            'source ~/ugv_ws/install/setup.bash && '
            'ros2 launch ugv_bringup bringup_lidar.launch.py use_rviz:=false'
        ])
        await asyncio.sleep(5)
    else:
        print("[启动] 底盘驱动已在运行，跳过")

    if not is_rosbridge_running():
        print("[启动] 启动 rosbridge...")
        rosbridge_proc = subprocess.Popen([
            'docker', 'exec', 'ugv_jetson_ros_humble', 'bash', '-c',
            'source /opt/ros/humble/setup.bash && '
            'source ~/ugv_ws/install/setup.bash && '
            'ros2 launch rosbridge_server rosbridge_websocket_launch.xml port:=9090 address:=0.0.0.0'
        ])
        await asyncio.sleep(2)
    else:
        print("[启动] rosbridge 已在运行，跳过")

    ros2_runtime = {
        "status": "ready",
        "bringup_proc": bringup_proc,
        "rosbridge_proc": rosbridge_proc,
    }
    app.state.ros2_runtime = ros2_runtime

    try:
        yield ros2_runtime
    finally:
        print("[关闭] 停止 rosbridge...")
        if rosbridge_proc:
            rosbridge_proc.terminate()
        print("[关闭] 停止底盘驱动...")
        if bringup_proc:
            bringup_proc.terminate()
        app.state.ros2_runtime = None
        print("[关闭] ROS2 服务已停止")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncExitStack() as stack:
        app.state.components = {}
        app.state.components["ros2_drivers"] = await stack.enter_async_context(
            ros2_drivers(app)
        )
        yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)


@app.get("/healthz", tags=["health"])
def healthz() -> dict[str, str]:
    return {"status": "ok", "env": settings.env}


app.include_router(workflow_router, prefix="/api/v1")