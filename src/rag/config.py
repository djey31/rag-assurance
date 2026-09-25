from __future__ import annotations
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    llm_provider: str = "ollama"
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "mistral:7b-instruct"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-5"
    openai_base_url: str = ""
    openai_api_key: str = ""
    openai_model: str = ""
    embedding_model: str = "intfloat/multilingual-e5-base"
    chroma_dir: str = ".chroma"
    top_k: int = 5

    class Config:
        env_file = ".env"

settings = Settings()
