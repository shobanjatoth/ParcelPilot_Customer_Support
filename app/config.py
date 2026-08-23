# from pydantic_settings import BaseSettings
# from functools import lru_cache


# class Settings(BaseSettings):
#     llm_provider: str = "gemini"
#     llm_model: str = "gemini-2.5-flash"
#     openrouter_api_key: str = ""
#     openrouter_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"  # Must have trailing slash here for Gemini
#     database_url: str = "sqlite:///./parcelpilot.db"
#     embedding_model: str = "all-MiniLM-L6-v2"
#     vector_store: str = "chromadb"
#     environment: str = "development"
#     log_level: str = "INFO"

#     model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


# @lru_cache
# def get_settings() -> Settings:
#     return Settings()



from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # LLM
    llm_provider: str = "gemini"
    llm_model: str = "gemini-3.5-flash"

    gemini_api_key: str = ""
    gemini_base_url: str = (
        "https://generativelanguage.googleapis.com/v1beta/openai"
    )

    # Database
    database_url: str = "sqlite:///./parcelpilot.db"

    # Embeddings
    embedding_model: str = "all-MiniLM-L6-v2"

    # Vector Store
    vector_store: str = "chromadb"

    # Application
    environment: str = "development"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()