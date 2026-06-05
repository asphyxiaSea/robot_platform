from functools import lru_cache
from typing import Literal

from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.types import Command


from app.core.config import settings
from app.workflows.voice_control.nodes.tool_node import robot_tools
from app.workflows.voice_control.state import VoiceControlState


_SYSTEM_PROMPT = """你是机器人语音控制助手，可以控制机器人的移动、灯光和云台，也可以进行日常对话。

可用能力：
- 移动控制：前进、后退、左转、右转、停止
- 灯光控制：开灯、关灯、单独控制左右灯
- 云台控制：水平转动、俯仰控制、归位
- 日常对话：回答问题

执行规则：
- 识别到明确控制指令时，直接调用对应工具执行，并用一句简短中文反馈结果
- 无法确定控制意图时，不调用任何工具，礼貌询问用户具体想做什么
- 用户在提问时，不调用任何工具，直接用简短中文回复
- 所有回复保持简短，适合语音播报
- 不要输出 JSON，不要输出多余解释
"""

@lru_cache(maxsize=1)
def _get_llm() -> ChatOllama:
    return ChatOllama(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=settings.voice_llm_temperature,
    )


_llm_with_tools = _get_llm().bind_tools(robot_tools)


def llm_node(state: VoiceControlState) -> Command[Literal["tools", "tts"]]:
    text = " ".join(str(state.get("text", "") or "").strip().split())

    if not text:
        return Command(
            goto="tts",
            update={**state, "messages": [AIMessage(content="我没有听清楚，请再说一遍。")]},
        )

    messages = [
        SystemMessage(content=_SYSTEM_PROMPT),
        HumanMessage(content=f"用户语音指令：{text}"),
    ]

    message: AIMessage = _llm_with_tools.invoke(messages)  # type: ignore
    print(f"[LLM] 输入: {text}")
    print(f"[LLM] tool_calls: {message.tool_calls}")

    goto = "tools" if message.tool_calls else "tts"

    return Command(
        goto=goto,
        update={**state, "messages": messages + [message]},
    )