import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # =========================================================
    # LLM
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

    database_url: str = (
        "postgresql+psycopg://"
        "parcelpilot:parcelpilot"
        "@localhost:5432/parcelpilot"
    )

    # =========================================================
    # JINA EMBEDDINGS
    # =========================================================

    jina_api_key: str = ""

    jina_base_url: str = (
        "https://api.jina.ai/v1/embeddings"
    )

    # IMPORTANT:
    # This must NOT be all-MiniLM-L6-v2.
    #
    # all-MiniLM-L6-v2 = local SentenceTransformer
    # jina-embeddings-v3 = Jina API
    # =========================================================

    embedding_model: str = "jina-embeddings-v3"

    # Jina embeddings dimension used by our VectorStore.
    embedding_dimension: int = 1024

    # =========================================================
    # Qdrant Cloud / Vector Store
    # =========================================================

    vector_store: str = "qdrant"

    qdrant_api: str = ""

    qdrant_endpoint: str = ""

    # Separate collection for Jina vectors.
    #
    # Do NOT use the old collection if it contains
    # all-MiniLM-L6-v2 384-dimensional vectors.
    # =========================================================

    qdrant_collection: str = (
        "parcelpilot_jina_documents"
    )

    # =========================================================
    # Application
    # =========================================================

    environment: str = "development"

    log_level: str = "INFO"

    # =========================================================
    # LangSmith
    # =========================================================

    langchain_tracing_v2: bool = True

    langchain_endpoint: str = (
        "https://api.smith.langchain.com"
    )

    langchain_api_key: str = ""

    langchain_project: str = (
        "parcelpilot-ai-agent"
    )

    # =========================================================
    # Logfire
    # =========================================================

    logfire_token: str = ""

    # =========================================================
    # Security
    # =========================================================

    jwt_secret: str = ""

    # =========================================================
    # CORS
    # =========================================================

    cors_origins: str = (
        "http://localhost:5173"
    )

    # =========================================================
    # Pydantic Settings
    # =========================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


# =============================================================
# SETTINGS SINGLETON
# =============================================================

@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
