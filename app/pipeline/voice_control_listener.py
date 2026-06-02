import ctypes
import threading
from uuid import uuid4

import numpy as np
import pyaudio
import sounddevice as sd
from piper.voice import PiperVoice

from app.core.config import settings
from app.workflows.voice_control.graph import voice_control_graph


ERROR_HANDLER_FUNC = ctypes.CFUNCTYPE(
    None,
    ctypes.c_char_p,
    ctypes.c_int,
    ctypes.c_char_p,
    ctypes.c_int,
    ctypes.c_char_p,
)


def _py_error_handler(*args):
    pass


ctypes.cdll.LoadLibrary("libasound.so.2").snd_lib_error_set_handler(
    ERROR_HANDLER_FUNC(_py_error_handler)
)

MIC_RATE = 48000
ASR_RATE = 16000
FRAMES = 4096
RESAMPLE_RATIO = MIC_RATE // ASR_RATE

VOLUME_THRESHOLD = settings.voice_volume_threshold
SILENCE_FRAMES = settings.voice_silence_frames


class VoiceControlListener:
    def __init__(self) -> None:
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._running = False
        self._session_id = ""

    def is_running(self) -> bool:
        return self._running and self._thread is not None and self._thread.is_alive()

    def session_id(self) -> str:
        return self._session_id

    def status(self) -> dict[str, str | bool]:
        return {
            "running": self.is_running(),
            "session_id": self._session_id,
        }

    def start(self) -> tuple[bool, str]:
        with self._lock:
            if self.is_running():
                return False, self._session_id

            self._session_id = f"voice-{uuid4().hex[:8]}"
            self._running = True
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()
            return True, self._session_id

    def stop(self) -> bool:
        with self._lock:
            was_running = self._running
            self._running = False
            return was_running

    def _speak(self, voice: PiperVoice, text: str) -> None:
        print(f"\n[TTS] {text}")
        audio = np.concatenate([chunk.audio_float_array for chunk in voice.synthesize(text)])
        audio *= 0.3
        sd.play(audio, voice.config.sample_rate)
        sd.wait()

    def _loop(self) -> None:
        print("开始实时语音助手监听...")
        print(f"当前会话: {self._session_id}")

        try:
            voice = PiperVoice.load(
                "models/zh_CN-huayan-medium.onnx",
                config_path="models/zh_CN-huayan-medium.onnx.json",
            )

            audio_interface = pyaudio.PyAudio()
            stream = audio_interface.open(
                rate=MIC_RATE,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                input_device_index=settings.audio_input_device_index,
                frames_per_buffer=FRAMES,
            )

            try:
                buffer: list[np.ndarray] = []
                silence_count = 0

                while self._running:
                    data = stream.read(FRAMES, exception_on_overflow=False)
                    audio = np.frombuffer(data, dtype=np.int16)
                    audio_16k = audio[::RESAMPLE_RATIO]

                    vol = float(np.abs(audio_16k).mean())
                    print(
                        f"[音量] {vol:.1f} buffer={len(buffer)} silence={silence_count}",
                        end="\r",
                    )

                    if vol < VOLUME_THRESHOLD:
                        silence_count += 1

                        if buffer and silence_count >= SILENCE_FRAMES:
                            full_audio = np.concatenate(buffer)
                            buffer.clear()
                            silence_count = 0

                            print("\n[工作流处理中...]")

                            result = voice_control_graph.invoke(
                                {
                                    "audio": full_audio,
                                    "trace": [],
                                }
                            )
                            text = result.get("text", "")
                            if text:
                                print(f"[识别] {text}")
                            response = result.get("response", "")
                            route = result.get("route", "fallback")
                            print(f"[路由] {route}")

                            if response:
                                self._speak(voice, response)

                        continue

                    silence_count = 0
                    buffer.append(audio_16k)
            finally:
                stream.stop_stream()
                stream.close()
                audio_interface.terminate()
        except Exception as exc:
            print(f"[监听异常] {exc}")
        finally:
            self._running = False


voice_control_listener = VoiceControlListener()
