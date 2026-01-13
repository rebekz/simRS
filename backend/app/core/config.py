from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SIMRS"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Sistem Informasi Manajemen Rumah Sakit"

    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="REFRESH_TOKEN_EXPIRE_DAYS")
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    # Redis
    REDIS_URL: str = Field(..., env="REDIS_URL")

    # MinIO/S3
    MINIO_ENDPOINT: str = Field(..., env="MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: str = Field(..., env="MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = Field(..., env="MINIO_SECRET_KEY")
    MINIO_SECURE: bool = False
    MINIO_BUCKET: str = "simrs"

    # Environment
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = False

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # BPJS Integration
    BPJS_CONSUMER_ID: Optional[str] = Field(default="", env="BPJS_CONSUMER_ID")
    BPJS_CONSUMER_SECRET: Optional[str] = Field(default="", env="BPJS_CONSUMER_SECRET")
    BPJS_BASE_URL: str = "https://apijkn.bpjs-kesehatan.go.id"
    BPJS_BASE_URL_VCLAIM: str = "https://new-api.bpjs-kesehatan.go.id:8080"

    # SATUSEHAT Integration
    SATUSEHAT_CLIENT_ID: Optional[str] = Field(default="", env="SATUSEHAT_CLIENT_ID")
    SATUSEHAT_CLIENT_SECRET: Optional[str] = Field(default="", env="SATUSEHAT_CLIENT_SECRET")
    SATUSEHAT_BASE_URL: str = "https://api-satusehat.kemkes.go.id"
    SATUSEHAT_AUTH_URL: str = "https://api-satusehat.kemkes.go.id/oauth2/v1"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Audit Log Encryption
    AUDIT_LOG_ENCRYPTION_KEY: Optional[str] = Field(default="", env="AUDIT_LOG_ENCRYPTION_KEY")

    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set[str] = {
        ".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx", ".xls", ".xlsx"
    }

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
