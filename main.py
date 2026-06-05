from contextlib import AsyncExitStack, asynccontextmanager

from fastapi import FastAPI

from app.api.voice_control import router as voice_control_router
from app.core.config import settings

import subprocess
import asyncio
import websocket


def is_rosbridge_running() -> bool:
    try:
        ws = websocket.WebSocket()
        ws.connect("ws://127.0.0.1:9090", timeout=2)
        ws.close()
        return True
    except Exception:
        return False


def is_bringup_running() -> bool:
    result = subprocess.run(
        ['docker', 'exec', 'ugv_jetson_ros_humble', 'bash', '-c',
         'source /opt/ros/humble/setup.bash && '
         'source /home/ws/ugv_ws/install/setup.bash && '
         'ros2 node list'],
        capture_output=True, text=True
    )
    return '/ugv_bringup' in result.stdout or 'ugv' in result.stdout

@asynccontextmanager
async def ros2_drivers(app: FastAPI):
    if not is_bringup_running():
        print("[启动] 启动底盘驱动...")
        subprocess.Popen([
            'docker', 'exec', 'ugv_jetson_ros_humble', 'bash', '-c',
            'source /opt/ros/humble/setup.bash && '
            'source /home/ws/ugv_ws/install/setup.bash && '
            'ros2 run ugv_bringup ugv_driver'
        ])
        await asyncio.sleep(5)
    else:
        print("[启动] 底盘驱动已在运行，跳过")

    if not is_rosbridge_running():
        print("[启动] 启动 rosbridge...")
        subprocess.Popen([
            'docker', 'exec', 'ugv_jetson_ros_humble', 'bash', '-c',
            'source /opt/ros/humble/setup.bash && '
            'source /home/ws/ugv_ws/install/setup.bash && '
            'ros2 run rosbridge_server rosbridge_websocket'
        ])
        await asyncio.sleep(2)
    else:
        print("[启动] rosbridge 已在运行，跳过")

    app.state.ros2_runtime = {"status": "ready"}
    yield


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with AsyncExitStack() as stack:
        await stack.enter_async_context(ros2_drivers(app))
        yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
)


@app.get("/healthz", tags=["health"])
def healthz() -> dict[str, str]:
    return {"status": "ok", "env": settings.env}


app.include_router(voice_control_router, prefix="/robot_platform")