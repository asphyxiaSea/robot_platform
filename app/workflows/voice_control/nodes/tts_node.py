import numpy as np
import sounddevice as sd
from langchain_core.messages import AIMessage, ToolMessage
from piper.voice import PiperVoice

from app.workflows.voice_control.state import VoiceControlState

_voice: PiperVoice | None = None


def _get_voice() -> PiperVoice:
    global _voice
    if _voice is None:
        _voice = PiperVoice.load(
            "models/zh_CN-huayan-medium.onnx",
            config_path="models/zh_CN-huayan-medium.onnx.json",
        )
    return _voice


def _speak(text: str) -> None:
    voice = _get_voice()
    audio = np.concatenate([
        chunk.audio_float_array for chunk in voice.synthesize(text)
    ])
    audio *= 0.2
    sd.play(audio, voice.config.sample_rate)
    sd.wait()


def tts_node(state: VoiceControlState) -> VoiceControlState:
    messages = state.get("messages", [])
    response = ""

    for msg in reversed(messages):
        if isinstance(msg, ToolMessage):
            response = str(msg.content).strip()
            break
        if isinstance(msg, AIMessage):
            response = str(msg.content).strip()
            break

    if not response:
        return state

    print(f"[TTS] {response}")
    try:
        _speak(response)
    except Exception as exc:
        print(f"[TTS错误] {exc}")

    return state