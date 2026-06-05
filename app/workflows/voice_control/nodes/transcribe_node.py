import json
import tempfile
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import numpy as np
import soundfile as sf

from app.core.config import settings
from app.workflows.voice_control.state import VoiceControlState


ASR_RATE = 16000


def transcribe_node(state: VoiceControlState) -> VoiceControlState:
    audio = state.get("audio")
    if audio is None or len(audio) == 0:
        return {**state, "text": ""}

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        sf.write(tmp.name, np.asarray(audio), ASR_RATE, format="WAV", subtype="PCM_16")
        tmp_path = tmp.name

    try:
        query = urlencode({"wav_path": tmp_path})
        with urlopen(f"{settings.funasr_url}?{query}", timeout=settings.funasr_timeout_s) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        text = str(payload.get("text", "")).strip()
        print(f"[ASR结果] {text}")
        return {**state, "text": text}
    finally:
        Path(tmp_path).unlink(missing_ok=True)