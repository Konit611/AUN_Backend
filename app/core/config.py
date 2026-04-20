from pydantic import computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "aun-back"
    DEBUG: bool = False
    FRONTEND_URL: str = "http://localhost:3000"

    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "aun"
    DB_PASSWORD: str = "changeme"
    DB_NAME: str = "aun"

    JWT_SECRET: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    AUTH_COOKIE_NAME: str = "access_token"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @computed_field
    @property
    def COOKIE_SECURE(self) -> bool:
        return not self.DEBUG

    model_config = {"env_file": ".env"}


settings = Settings()
