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

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = {"env_file": ".env"}


settings = Settings()
