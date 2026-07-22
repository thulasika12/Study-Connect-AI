"""
Application configuration loaded from environment variables (.env file).
Uses pydantic-settings so values are validated and typed.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Learnfy AI"
    ENVIRONMENT: str = "development"
    FRONTEND_URL: str = "http://localhost:5173"
    UPLOAD_DIR: str = "app/uploads"

    # Database
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/study_connect_ai"

    # JWT
    JWT_SECRET_KEY: str = "insecure_dev_secret_change_me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_RESET_EXPIRE_MINUTES: int = 30
    MAX_UPLOAD_SIZE_MB: int = 20

    # Google Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
