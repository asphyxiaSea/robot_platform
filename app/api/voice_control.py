from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.pipeline.voice_control_recorder import voice_control_recorder

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


@router.post("/start", response_model=VoiceControlStartResponse)
def start_voice_control_recorder() -> VoiceControlStartResponse:
    try:
        started, session_id = voice_control_recorder.start()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"voice control recorder start failed: {exc}") from exc

    if started:
        message = "录音已开始，3秒后会自动停止并处理语音。"
    else:
        message = "录音已在进行中。"

    return VoiceControlStartResponse(
        started=started,
        running=voice_control_recorder.is_running(),
        session_id=session_id,
        message=message,
    )


@router.post("/stop", response_model=VoiceControlStopResponse)
def stop_voice_control_recorder() -> VoiceControlStopResponse:
    try:
        stopped = voice_control_recorder.stop()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"voice control recorder stop failed: {exc}") from exc

    if stopped:
        message = "录音已手动停止，正在处理本次语音。"
    else:
        message = "当前没有正在进行的录音。"

    return VoiceControlStopResponse(
        stopped=stopped,
        running=voice_control_recorder.is_running(),
        session_id=voice_control_recorder.session_id(),
        message=message,
    )
