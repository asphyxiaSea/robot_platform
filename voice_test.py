import ctypes
import json

import numpy as np
import pyaudio
import sounddevice as sd

from vosk import Model, KaldiRecognizer
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

VOLUME_THRESHOLD = 80

# =========================
# 加载模型
# =========================
rec = KaldiRecognizer(
    Model("models/vosk-model-cn-0.22"),
    ASR_RATE
)

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
# TTS
# =========================
def speak(text):

    print(f"\n[TTS] {text}")

    audio = np.concatenate([
        chunk.audio_float_array
        for chunk in voice.synthesize(text)
    ])

    audio *= 0.3

    sd.play(audio, voice.config.sample_rate)

    sd.wait()

# =========================
# 主循环
# =========================
print("开始实时语音助手...")

while True:

    data = stream.read(FRAMES, exception_on_overflow=False)

    audio = np.frombuffer(data, dtype=np.int16)

    # 音量过小直接跳过
    if np.abs(audio).mean() < VOLUME_THRESHOLD:
        continue

    # 简单降采样
    audio = audio[::RESAMPLE_RATIO]

    # ASR
    if rec.AcceptWaveform(audio.tobytes()):

        text = json.loads(
            rec.Result()
        ).get("text", "").strip()

        if text:

            print(f"\n[识别] {text}")

            speak(text)

    else:

        partial = json.loads(
            rec.PartialResult()
        ).get("partial", "")

        if partial:
            print(f"[实时中] {partial}", end="\r")