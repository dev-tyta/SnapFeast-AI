import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # Database settings
    DATABASE_USER: str = os.getenv("PG_USER")
    DATABASE_PASSWORD: str = os.getenv("PG_PASSWORD")
    DATABASE_HOST: str = os.getenv("PG_HOST")
    DATABASE_PORT: str = os.getenv("PG_PORT")
    DATABASE_NAME: str = os.getenv("PG_NAME")
    
    # JWT settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # Application settings
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ALLOWED_HOSTS: list = os.getenv("ALLOWED_HOSTS", "*").split(",")

    # Face recognition settings
    FACE_RECOGNITION_THRESHOLD: float = float(os.getenv("FACE_RECOGNITION_THRESHOLD", "0.6"))

    @property
    def DATABASE_URL(self) -> str:
        user = quote_plus(self.DATABASE_USER)
        password = quote_plus(self.DATABASE_PASSWORD)
        return f"postgresql://{user}:{password}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}?sslmode=require"

    class Config:
        env_file = ".env"

def get_settings() -> Settings:
    return Settings()
