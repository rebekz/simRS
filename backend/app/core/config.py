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
    BPJS_USER_KEY: Optional[str] = Field(default="", env="BPJS_USER_KEY")
    BPJS_SERVICE_NAME: str = Field(default="SIMRS", env="BPJS_SERVICE_NAME")
    BPJS_BASE_URL: str = "https://apijkn.bpjs-kesehatan.go.id"
    BPJS_BASE_URL_VCLAIM: str = "https://new-api.bpjs-kesehatan.go.id:8080"
    BPJS_API_URL: str = "https://apijkn.bpjs-kesehatan.go.id/vclaim-rest"
    BPJS_APLICARE_URL: str = "https://apijkn.bpjs-kesehatan.go.id/aplicarews"

    # SATUSEHAT Integration
    SATUSEHAT_CLIENT_ID: Optional[str] = Field(default="", env="SATUSEHAT_CLIENT_ID")
    SATUSEHAT_CLIENT_SECRET: Optional[str] = Field(default="", env="SATUSEHAT_CLIENT_SECRET")
    SATUSEHAT_BASE_URL: str = "https://api-satusehat.kemkes.go.id"
    SATUSEHAT_AUTH_URL: str = "https://api-satusehat.kemkes.go.id/oauth2/v1"
    SATUSEHAT_API_URL: str = "https://api-satusehat.kemkes.go.id/fhir-r4/v1"

    # Logging
    LOG_LEVEL: str = "INFO"

    # Audit Log Encryption
    AUDIT_LOG_ENCRYPTION_KEY: Optional[str] = Field(default="", env="AUDIT_LOG_ENCRYPTION_KEY")

    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set[str] = {
        ".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx", ".xls", ".xlsx"
    }

    # Notification Channels
    SMS_PROVIDER: str = Field(default="mock", env="SMS_PROVIDER")  # twilio, nexmo, mock
    SMS_FROM_NUMBER: str = Field(default="+1234567890", env="SMS_FROM_NUMBER")
    TWILIO_ACCOUNT_SID: Optional[str] = Field(default="", env="TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = Field(default="", env="TWILIO_AUTH_TOKEN")
    NEXMO_API_KEY: Optional[str] = Field(default="", env="NEXMO_API_KEY")
    NEXMO_API_SECRET: Optional[str] = Field(default="", env="NEXMO_API_SECRET")

    SMTP_HOST: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: str = Field(default="", env="SMTP_USERNAME")
    SMTP_PASSWORD: str = Field(default="", env="SMTP_PASSWORD")
    SMTP_USE_TLS: bool = Field(default=True, env="SMTP_USE_TLS")
    SMTP_FROM_EMAIL: str = Field(default="noreply@simrs.hospital", env="SMTP_FROM_EMAIL")
    SMTP_FROM_NAME: str = Field(default="SIMRS Hospital", env="SMTP_FROM_NAME")

    PUSH_PROVIDER: str = Field(default="mock", env="PUSH_PROVIDER")  # firebase, apns, mock
    FIREBASE_SERVER_KEY: Optional[str] = Field(default="", env="FIREBASE_SERVER_KEY")
    APNS_KEY_ID: Optional[str] = Field(default="", env="APNS_KEY_ID")
    APNS_TEAM_ID: Optional[str] = Field(default="", env="APNS_TEAM_ID")

    WHATSAPP_API_URL: str = Field(default="https://graph.facebook.com/v17.0", env="WHATSAPP_API_URL")
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = Field(default="", env="WHATSAPP_PHONE_NUMBER_ID")
    WHATSAPP_ACCESS_TOKEN: Optional[str] = Field(default="", env="WHATSAPP_ACCESS_TOKEN")

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore",  # Allow extra env vars from Docker
    }


settings = Settings()
