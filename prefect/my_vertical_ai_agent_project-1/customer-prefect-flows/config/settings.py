"""Application settings and configuration."""

import os
from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings."""
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Prefect Configuration
    prefect_api_url: Optional[str] = Field(default=None, env="PREFECT_API_URL")
    prefect_api_key: Optional[str] = Field(default=None, env="PREFECT_API_KEY")
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_org_id: Optional[str] = Field(default=None, env="OPENAI_ORG_ID")
    
    # LangChain Configuration
    langchain_tracing_v2: bool = Field(default=False, env="LANGCHAIN_TRACING_V2")
    langchain_api_key: Optional[str] = Field(default=None, env="LANGCHAIN_API_KEY")
    langchain_project: str = Field(default="customer-prefect-flows", env="LANGCHAIN_PROJECT")
    
    # CrewAI Configuration
    crewai_telemetry_opt_out: bool = Field(default=True, env="CREWAI_TELEMETRY_OPT_OUT")
    
    # Customer Configuration
    customer_name: str = Field(..., env="CUSTOMER_NAME")
    customer_api_url: Optional[str] = Field(default=None, env="CUSTOMER_API_URL")
    customer_api_key: Optional[str] = Field(default=None, env="CUSTOMER_API_KEY")
    
    # Database Configuration
    database_url: Optional[str] = Field(default=None, env="DATABASE_URL")
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Global settings instance
settings = get_settings()
