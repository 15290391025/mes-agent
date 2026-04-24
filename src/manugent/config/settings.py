"""ManuGent Configuration Management.

Handles loading configuration from environment variables and config files.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings


class LLMSettings(BaseSettings):
    """LLM provider configuration."""
    provider: str = Field(default="openai", alias="LLM_PROVIDER")
    api_key: str = Field(default="", alias="LLM_API_KEY")
    model: str = Field(default="gpt-4o", alias="LLM_MODEL")
    base_url: str = Field(default="", alias="LLM_BASE_URL")

    # Ollama settings
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="qwen2.5:72b", alias="OLLAMA_MODEL")

    model_config = {"env_file": ".env", "extra": "ignore"}

    def get_llm(self) -> Any:
        """Create LLM instance based on provider."""
        if self.provider == "openai":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=self.model,
                api_key=self.api_key,
                base_url=self.base_url or None,
            )
        elif self.provider == "anthropic":
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=self.model,
                api_key=self.api_key,
            )
        elif self.provider == "ollama":
            from langchain_ollama import ChatOllama
            return ChatOllama(
                model=self.ollama_model,
                base_url=self.ollama_base_url,
            )
        elif self.provider == "qwen":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=self.model or "qwen-max",
                api_key=self.api_key,
                base_url=self.base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1",
            )
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")


class DatabaseSettings(BaseSettings):
    """Database configuration."""
    database_url: str = Field(
        default="postgresql+asyncpg://manugent:manugent@localhost:5432/manugent",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    memory_db_path: str = Field(default="data/manugent-memory.sqlite3", alias="MEMORY_DB_PATH")

    model_config = {"env_file": ".env", "extra": "ignore"}


class MESSettings(BaseSettings):
    """MES connection configuration."""
    mes_type: str = Field(default="demo", alias="MES_TYPE")
    mes_url: str = Field(default="demo://smt-factory", alias="MES_BASE_URL")
    mes_token: str = Field(default="", alias="MES_API_TOKEN")
    mes_username: str = Field(default="", alias="MES_USERNAME")
    mes_password: str = Field(default="", alias="MES_PASSWORD")
    mes_timeout: int = Field(default=30, alias="MES_TIMEOUT")

    model_config = {"env_file": ".env", "extra": "ignore"}


class AppSettings(BaseSettings):
    """Application-level settings."""
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    mcp_port: int = Field(default=8001, alias="MCP_PORT")
    jwt_secret: str = Field(default="change-me", alias="JWT_SECRET")
    audit_enabled: bool = Field(default=True, alias="AUDIT_ENABLED")
    edge_mode: bool = Field(default=False, alias="EDGE_MODE")

    model_config = {"env_file": ".env", "extra": "ignore"}


class Settings:
    """Combined settings container."""

    def __init__(self, env_file: str | Path | None = None) -> None:
        env_path = Path(env_file) if env_file else Path(".env")
        if env_path.exists():
            from dotenv import load_dotenv
            load_dotenv(env_path)

        self.llm = LLMSettings()
        self.db = DatabaseSettings()
        self.mes = MESSettings()
        self.app = AppSettings()

    @classmethod
    def from_env(cls) -> Settings:
        """Create settings from environment variables."""
        return cls()
