"""Application settings — single source of truth loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global settings shared across all Sentinel services."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    mongodb_uri: str = "mongodb://localhost:27017/sentinel"
    groq_api_key: str = ""
    gemini_api_key: str = ""
    neo4j_uri: str = ""
    neo4j_user: str = ""
    neo4j_password: str = ""

    detector_url: str = "http://localhost:8001"
    investigator_url: str = "http://localhost:8002"
    hypothesis_ranker_url: str = "http://localhost:8003"
    narrator_url: str = "http://localhost:8004"
    critic_url: str = "http://localhost:8005"
    toy_system_url: str = "http://localhost:8080"

    graph_backend: str = "networkx"  # "networkx" | "neo4j"
    llm_primary: str = "groq"  # "groq" | "gemini"
