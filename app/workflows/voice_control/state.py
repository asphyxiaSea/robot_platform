from typing import TypedDict

import numpy as np


class VoiceControlState(TypedDict, total=False):
    audio: np.ndarray
    text: str
    normalized_text: str
    intent: str
    route: str
    action: str
    linear_x: float
    angular_z: float
    duration_s: float
    executed: bool
    safety_stop_applied: bool
    response: str
    llm_raw: str
    trace: list[str]
    error: str
