from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    cors_origins: str = 'http://localhost:5173,http://127.0.0.1:5173'
    crossref_contact: str = ''
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

@lru_cache

def get_settings() -> Settings:
    settings = Settings()
    if len(settings.jwt_secret) < 32:
        raise ValueError('JWT_SECRET must contain 32 or more characters')
    return settings
