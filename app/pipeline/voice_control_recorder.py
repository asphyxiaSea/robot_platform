import ctypes
import threading
from uuid import uuid4

import numpy as np
import pyaudio

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
RECORD_SECONDS = 3.0


class VoiceControlRecorder:
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

    def _run_workflow(self, full_audio: np.ndarray) -> None:
        print("\n[工作流处理中...]")
        try:
            result = voice_control_graph.invoke({"audio": full_audio})

            text = result.get("text", "")
            if text:
                print(f"[识别] {text}")

            messages = result.get("messages", [])
            if messages:
                last = messages[-1]
                content = str(getattr(last, "content", "")).strip()
                if content:
                    print(f"[反馈] {content}")
        except Exception as exc:
            print(f"[工作流异常] {exc}")

    def _loop(self) -> None:
        print(f"开始录音，固定时长 {RECORD_SECONDS:.0f} 秒...")
        print(f"当前会话: {self._session_id}")

        try:
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
                target_chunks = max(1, int(RECORD_SECONDS * MIC_RATE / FRAMES))

                while self._running and len(buffer) < target_chunks:
                    data = stream.read(FRAMES, exception_on_overflow=False)
                    audio = np.frombuffer(data, dtype=np.int16)
                    audio_16k = audio[::RESAMPLE_RATIO]
                    buffer.append(audio_16k)

                    sec = len(buffer) * FRAMES / MIC_RATE
                    print(f"[录音中] {sec:.1f}s", end="\r")

                print("\n[录音结束]")

                if buffer:
                    full_audio = np.concatenate(buffer)
                    self._run_workflow(full_audio)
                else:
                    print("\n[录音结束] 未采集到有效音频")
            finally:
                stream.stop_stream()
                stream.close()
                audio_interface.terminate()
        except Exception as exc:
            print(f"[录音异常] {exc}")
        finally:
            self._running = False


voice_control_recorder = VoiceControlRecorder()