"""
config module
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = BASE_DIR / ".env"
class Settings(BaseSettings):
    """
    Load value from the .env file
    """
    model_config = SettingsConfigDict(env_file=str(ENV_FILE), env_file_encoding="utf-8")

    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 90

    APP_NAME: str = "Converto"
    DEBUG: bool = True

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLINET_SECRET: str

settings = Settings() # type: ignore
