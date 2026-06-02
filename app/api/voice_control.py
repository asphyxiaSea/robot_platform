from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.pipeline.voice_control_listener import voice_control_listener

router = APIRouter(prefix="/voice-control", tags=["voice-control"])


class VoiceControlStartResponse(BaseModel):
    started: bool
    running: bool
    session_id: str
    message: str


class VoiceControlStopResponse(BaseModel):
    stopped: bool
    running: bool
    session_id: str
    message: str


class VoiceControlStatusResponse(BaseModel):
    running: bool
    session_id: str


@router.post("/start", response_model=VoiceControlStartResponse)
def start_voice_control_listener() -> VoiceControlStartResponse:
    try:
        started, session_id = voice_control_listener.start()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"voice control listener start failed: {exc}") from exc

    if started:
        message = "语音监听已启动，检测到语音后会自动触发工作流控制小车。"
    else:
        message = "语音监听已在运行中。"

    return VoiceControlStartResponse(
        started=started,
        running=voice_control_listener.is_running(),
        session_id=session_id,
        message=message,
    )


@router.post("/stop", response_model=VoiceControlStopResponse)
def stop_voice_control_listener() -> VoiceControlStopResponse:
    try:
        stopped = voice_control_listener.stop()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"voice control listener stop failed: {exc}") from exc

    if stopped:
        message = "语音监听已停止。"
    else:
        message = "语音监听当前未运行。"

    return VoiceControlStopResponse(
        stopped=stopped,
        running=voice_control_listener.is_running(),
        session_id=voice_control_listener.session_id(),
        message=message,
    )


@router.get("/status", response_model=VoiceControlStatusResponse)
def get_voice_control_listener_status() -> VoiceControlStatusResponse:
    status = voice_control_listener.status()
    return VoiceControlStatusResponse(
        running=bool(status["running"]),
        session_id=str(status["session_id"]),
    )
