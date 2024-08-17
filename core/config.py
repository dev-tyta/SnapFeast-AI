import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote_plus
from pydantic_settings.base import BaseSettingsModel

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettingsModel):
    # DATABASE_URL: str
    # DATABASE_NAME: str
    # DATABASE_USER: str
    # DATABASE_PASSWORD: str
    # DATABASE_HOST: str
    # DATABASE_PORT: str
    # DATABASE_URL: str
    # DATABASE_URL = f"postgresql://{DATABASE_USER}:{quote_plus(DATABASE_PASSWORD)}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv("ACCESS_TOKEN")

def get_settings():
    return Settings()