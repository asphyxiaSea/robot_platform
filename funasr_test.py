import ctypes
import tempfile
from pathlib import Path

import numpy as np
import pyaudio
import sounddevice as sd
import soundfile as sf
from requests.api import get
from requests.exceptions import RequestException

from piper.voice import PiperVoice

# =========================
# 关闭 ALSA 警告
# =========================
ERROR_HANDLER_FUNC = ctypes.CFUNCTYPE(
    None,
    ctypes.c_char_p,
    ctypes.c_int,
    ctypes.c_char_p,
    ctypes.c_int,
    ctypes.c_char_p,
)

def py_error_handler(*args):
    pass

ctypes.cdll.LoadLibrary("libasound.so.2") \
    .snd_lib_error_set_handler(ERROR_HANDLER_FUNC(py_error_handler))

# =========================
# 配置
# =========================
MIC_RATE = 48000
ASR_RATE = 16000
FRAMES = 4096

RESAMPLE_RATIO = MIC_RATE // ASR_RATE

VOLUME_THRESHOLD = 200
SILENCE_FRAMES = 8  # 连续 N 帧静音后触发识别

FUNASR_URL = "http://localhost:8010/funasr/transcribe/path"

# =========================
# 加载模型
# =========================
voice = PiperVoice.load(
    "models/zh_CN-huayan-medium.onnx",
    config_path="models/zh_CN-huayan-medium.onnx.json"
)

# =========================
# 麦克风
# =========================
stream = pyaudio.PyAudio().open(
    rate=MIC_RATE,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    input_device_index=1,
    frames_per_buffer=FRAMES
)

# =========================
# ASR
# =========================
def transcribe(audio: np.ndarray) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        sf.write(tmp.name, audio, ASR_RATE, format="WAV", subtype="PCM_16")
        tmp_path = tmp.name

    try:
        resp = get(
            FUNASR_URL,
            params={"wav_path": tmp_path},
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json().get("text", "").strip()
    except RequestException as e:
        print(f"[ASR错误] {e}")
        return ""
    finally:
        Path(tmp_path).unlink(missing_ok=True)

# =========================
# TTS
# =========================
def speak(text: str) -> None:
    print(f"\n[TTS] {text}")

    audio = np.concatenate([
        chunk.audio_float_array
        for chunk in voice.synthesize(text)
    ])

    audio *= 0.3

    sd.play(audio, voice.config.sample_rate)
    sd.wait()

# =========================
# 音频缓冲
# =========================
buffer: list[np.ndarray] = []
silence_count = 0

# =========================
# 主循环
# =========================
print("开始实时语音助手...")

while True:

    data = stream.read(FRAMES, exception_on_overflow=False)
    audio = np.frombuffer(data, dtype=np.int16)

    audio_16k = audio[::RESAMPLE_RATIO]

    vol = np.abs(audio_16k).mean()
    print(f"[音量] {vol:.1f} buffer={len(buffer)} silence={silence_count}", end="\r")

    if vol < VOLUME_THRESHOLD:
        silence_count += 1

        if buffer and silence_count >= SILENCE_FRAMES:
            full_audio = np.concatenate(buffer)
            buffer.clear()
            silence_count = 0

            print("\n[识别中...]")
            text = transcribe(full_audio)
            print(f"[识别结果] '{text}'")

            if text:
                print(f"\n[识别] {text}")
                speak(text)
    else:
        silence_count = 0
        buffer.append(audio_16k)
        print(f"\n[录音中] buffer帧数={len(buffer)}")