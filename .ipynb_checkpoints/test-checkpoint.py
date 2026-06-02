import ctypes

ERROR_HANDLER_FUNC = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_int,
                                       ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p)
def py_error_handler(filename, line, function, err, fmt): pass
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
asound = ctypes.cdll.LoadLibrary("libasound.so.2")
asound.snd_lib_error_set_handler(c_error_handler)

from vosk import Model, KaldiRecognizer
import pyaudio
import json
import numpy as np


# ASR 初始化
MIC_RATE = 48000
VOSK_RATE = 16000
FRAMES = 4096
RESAMPLE_RATIO = MIC_RATE // VOSK_RATE

VOLUME_THRESHOLD = 80
SILENCE_LIMIT = 8
silence_count = 0

model = Model("models/vosk-model-cn-0.22")
rec = KaldiRecognizer(model, VOSK_RATE)

pa = pyaudio.PyAudio()
stream = pa.open(
    rate=MIC_RATE,
    channels=1,
    format=pyaudio.paInt16,
    input=True,
    input_device_index=1,
    frames_per_buffer=FRAMES
)

print("开始实时转文字，请说话...")
while True:
    data = stream.read(FRAMES, exception_on_overflow=False)
    audio = np.frombuffer(data, dtype=np.int16)

    volume = np.abs(audio).mean()
    if volume < VOLUME_THRESHOLD:
        silence_count += 1
        if silence_count > SILENCE_LIMIT:
            continue
    else:
        silence_count = 0

    audio_resampled = audio[::RESAMPLE_RATIO]
    data_resampled = audio_resampled.tobytes()

    if rec.AcceptWaveform(data_resampled):
        result = json.loads(rec.Result())
        text = result.get("text", "")
        if text:
            print(f"[完整句] {text}")
    else:
        partial = json.loads(rec.PartialResult())
        partial_text = partial.get("partial", "")
        if partial_text:
            print(f"[实时中] {partial_text}", end="\r")

