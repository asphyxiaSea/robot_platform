from typing import Annotated, TypedDict
import numpy as np
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class VoiceControlState(TypedDict, total=False):
    audio: np.ndarray
    text: str
    messages: Annotated[list[BaseMessage], add_messages]