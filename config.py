from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # AI Configuration
    ai_provider: str = "openai"  # "openai", "azure_openai", or "anthropic"
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    anthropic_model: str = "claude-3-sonnet-20240229"
    
    # Azure OpenAI Configuration
    azure_openai_endpoint: Optional[str] = None
    azure_openai_api_key: Optional[str] = None
    azure_openai_deployment: Optional[str] = None
    azure_openai_api_version: str = "2024-02-01"
    
    # Playwright Configuration
    headless: bool = True
    browser_type: str = "chromium"  # "chromium", "firefox", "webkit"
    timeout: int = 30000
    
    # Cache Configuration
    cache_file: str = "element_cache.json"
    
    # Logging Configuration
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()