"""Application settings and configuration."""

import os
from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings."""
    
    # Prefect settings
    prefect_api_url: Optional[str] = Field(
        default=None,
        description="Prefect API URL"
    )
    prefect_api_key: Optional[str] = Field(
        default=None,
        description="Prefect API key"
    )
    
    # OpenAI settings
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )
    
    # LangChain settings
    langchain_tracing_v2: bool = Field(
        default=False,
        description="Enable LangChain tracing"
    )
    langchain_api_key: Optional[str] = Field(
        default=None,
        description="LangChain API key"
    )
    langchain_project: str = Field(
        default="customer-flows",
        description="LangChain project name"
    )
    
    # Application settings
    environment: str = Field(
        default="development",
        description="Application environment"
    )
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    # Database/Storage settings (if needed)
    database_url: Optional[str] = Field(
        default=None,
        description="Database URL for persistence"
    )
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
