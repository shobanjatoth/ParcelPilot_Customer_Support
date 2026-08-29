import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # =========================================================
    # LLM (Core Agent / Gemini Configuration)
    # =========================================================

    llm_provider: str = "gemini"
    llm_model: str = "gemini-3.6-flash"

    gemini_api_key: str = ""
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai"

    # =========================================================
    # LLM Judge / Ragas Evaluation Configuration
    # =========================================================

    eval_llm_provider: str = "gemini"
    eval_llm_model: str = "gemini-3.6-flash"
    gemini_judge_api_key: str = ""
    gemini_judge_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai"
    eval_temperature: float = 0.0
    eval_max_tokens: int = 2048

    # =========================================================
    # PostgreSQL
    # =========================================================

    database_url: str = "postgresql+psycopg://parcelpilot:parcelpilot@localhost:5432/parcelpilot"

    # =========================================================
    # Embeddings
    # =========================================================

    embedding_model: str = "all-MiniLM-L6-v2"

    # =========================================================
    # Qdrant Cloud / Vector Store
    # =========================================================

    vector_store: str = "qdrant"

    qdrant_api: str = ""
    qdrant_endpoint: str = ""
    qdrant_collection: str = "parcelpilot_documents"

    # =========================================================
    # Application
    # =========================================================

    environment: str = "development"
    log_level: str = "INFO"

    # =========================================================
    # LangSmith
    # =========================================================

    langchain_tracing_v2: bool = True
    langchain_endpoint: str = "https://api.smith.langchain.com"
    langchain_api_key: str = ""
    langchain_project: str = "parcelpilot-ai-agent"

    # =========================================================
    # Logfire
    # =========================================================

    logfire_token: str = ""

    # =========================================================
    # Security
    # =========================================================

    jwt_secret: str = ""

    # =========================================================
    # Frontend / CORS
    # =========================================================

    cors_origins: str = "http://localhost:5173"

    # =========================================================
    # Pydantic Settings Configuration
    # =========================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()