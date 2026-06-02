from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Robot Platform Workflow API"
    app_version: str = "0.1.0"
    env: str = "dev"
    funasr_url: str = "http://localhost:8010/funasr/transcribe/path"
    funasr_timeout_s: int = 10
    audio_input_device_index: int = 1
    voice_volume_threshold: float = 200.0
    voice_silence_frames: int = 8
    ollama_base_url: str = "https://oa1.gxlky.com.cn/ollama"
    ollama_model: str = "llama3.1:8b"
    ollama_timeout_s: int = 20
    voice_llm_temperature: float = 0.1

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
