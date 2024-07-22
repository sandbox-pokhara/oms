from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class Environment(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    DEBUG: bool = True
    POSTGRES_HOST: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_DB: str = "oms"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_PORT: int = 5432
    ALLOWED_HOSTS: str = "*"
    CSRF_TRUSTED_ORIGINS: str = "http://127.0.0.1:8000"
    SECRET_KEY: str = (
        "django-insecure-#p!k!t6n8j#b6a&!q$+n+u0m&-m8n0j0!5#*b!b6p0t0c!+a+"
    )


ENV = Environment()
