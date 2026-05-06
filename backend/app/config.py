from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str

    JWT_SECRET_KEY: str = "SUPER_SECRET_KEY"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    REDIS_URL: str = "redis://localhost:6379"

    OPENAI_API_KEY: str = ""
    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""
    RAZORPAY_KEY_ID: str = ""
    RAZORPAY_KEY_SECRET: str = ""
    SENTRY_DSN: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"   # IMPORTANT: prevents crash if extra env vars exist
    )


settings = Settings()