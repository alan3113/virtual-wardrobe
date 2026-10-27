from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    database_url: str = 'postgresql+psycopg://wardrobe:wardrobe@localhost:5432/wardrobe'
    secret_key: str = 'change-me-in-production-use-a-long-key'
    access_token_minutes: int = 1440
    cors_origins: str = 'http://localhost:5173'
    upload_dir: Path = Path('uploads')
    public_base_url: str = 'http://localhost:8000'
    max_upload_bytes: int = 8 * 1024 * 1024


settings = Settings()
