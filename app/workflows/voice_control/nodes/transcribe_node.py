import json
import tempfile
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import numpy as np
import soundfile as sf
import httpx

from app.core.config import settings
from app.workflows.voice_control.state import VoiceControlState


ASR_RATE = 16000


### 以下是使用远程的 FunASR 服务进行语音转文本的实现。
def transcribe_node(state: VoiceControlState) -> VoiceControlState:
    audio = state.get("audio")
    if audio is None or len(audio) == 0:
        return {**state, "text": ""}

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        sf.write(tmp.name, np.asarray(audio), ASR_RATE, format="WAV", subtype="PCM_16")
        tmp_path = tmp.name

    try:
        with open(tmp_path, "rb") as f:
            with httpx.Client() as client:
                resp = client.post(
                    settings.remote_funasr_url,
                    files={"file": ("audio.wav", f, "audio/wav")},
                    timeout=settings.funasr_timeout_s,
                )
        text = str(resp.json().get("text", "")).strip()
        print(f"[ASR结果] {text}")
        return {**state, "text": text}
    finally:
        Path(tmp_path).unlink(missing_ok=True)


### 以下是使用本地的 FunASR 服务进行语音转文本的实现。
# def transcribe_node(state: VoiceControlState) -> VoiceControlState:
#     audio = state.get("audio")
#     if audio is None or len(audio) == 0:
#         return {**state, "text": ""}

#     with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
#         sf.write(tmp.name, np.asarray(audio), ASR_RATE, format="WAV", subtype="PCM_16")
#         tmp_path = tmp.name

#     try:
#         query = urlencode({"wav_path": tmp_path})
#         with urlopen(f"{settings.funasr_url}?{query}", timeout=settings.funasr_timeout_s) as resp:
#             payload = json.loads(resp.read().decode("utf-8"))
#         text = str(payload.get("text", "")).strip()
#         print(f"[ASR结果] {text}")
#         return {**state, "text": text}
#     finally:
#         Path(tmp_path).unlink(missing_ok=True)



### 以下是使用 Vosk 替代 FunASR 的实现。


# import ctypes
# import json

# import numpy as np
# from vosk import Model, KaldiRecognizer

# from app.core.config import settings
# from app.workflows.voice_control.state import VoiceControlState

# # 关闭 ALSA 警告
# ERROR_HANDLER_FUNC = ctypes.CFUNCTYPE(
#     None, ctypes.c_char_p, ctypes.c_int,
#     ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p,
# )
# ctypes.cdll.LoadLibrary("libasound.so.2").snd_lib_error_set_handler(
#     ERROR_HANDLER_FUNC(lambda *args: None)
# )

# ASR_RATE = 16000

# # 模型只加载一次
# _recognizer = KaldiRecognizer(
#     Model(settings.vosk_model_path),
#     ASR_RATE
# )


# def transcribe_node(state: VoiceControlState) -> VoiceControlState:
#     audio = state.get("audio")
#     if audio is None or len(audio) == 0:
#         return {**state, "text": ""}

#     audio_bytes = np.asarray(audio, dtype=np.int16).tobytes()

#     if _recognizer.AcceptWaveform(audio_bytes):
#         text = json.loads(_recognizer.Result()).get("text", "").strip()
#     else:
#         text = json.loads(_recognizer.PartialResult()).get("partial", "").strip()

#     print(f"[ASR结果] {text}")
#     return {**state, "text": text}