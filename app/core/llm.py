from functools import lru_cache

from langchain_ollama import ChatOllama

from app.core.config import settings


@lru_cache(maxsize=1)
def get_voice_control_llm() -> ChatOllama:
    return ChatOllama(
        model=settings.ollama_model,
        base_url=settings.ollama_base_url,
        temperature=settings.voice_llm_temperature,
        client_kwargs={"timeout": settings.ollama_timeout_s},
    )
