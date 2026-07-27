from contextlib import AsyncExitStack, asynccontextmanager

from fastapi import FastAPI

from app.api.voice_control import router as voice_control_router
from app.core.config import settings
from app.core.docker_ros2 import DockerROS2

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


@asynccontextmanager
async def ros2_drivers(app: FastAPI):
    if not DockerROS2.node_running("/ugv_driver"):
        print("[启动] 启动 ugv_driver...")
        DockerROS2.run_bg("ros2 run ugv_bringup ugv_driver")
        await asyncio.sleep(3)
    else:
        print("[启动] ugv_driver 已在运行，跳过")

    if not is_rosbridge_running():
        print("[启动] 启动 rosbridge...")
        DockerROS2.run_bg("ros2 run rosbridge_server rosbridge_websocket")
        await asyncio.sleep(3)
    else:
        print("[启动] rosbridge 已在运行，跳过")

    if not DockerROS2.node_running("/slam_toolbox"):
        print("[启动] 启动 slam_nav...")
        DockerROS2.run_bg("ros2 launch ugv_nav slam_nav.launch.py use_rviz:=false")
        await asyncio.sleep(10)
    else:
        print("[启动] slam_nav 已在运行，跳过")

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