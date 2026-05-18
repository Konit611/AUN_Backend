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
    # Empty for local docker postgres; set to "require" (or stricter) when
    # connecting to managed Postgres services like Supabase that enforce TLS.
    DB_SSLMODE: str = ""

    JWT_SECRET: str = "dev-secret-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    AUTH_COOKIE_NAME: str = "access_token"
    # Set to ".aunsake.com" in prod so the cookie is shared between the
    # frontend (aunsake.com) and the backend (api.aunsake.com). Leave empty
    # in local dev — the cookie is host-only and stays on localhost.
    COOKIE_DOMAIN: str = ""

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        base = (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
        if self.DB_SSLMODE:
            return f"{base}?sslmode={self.DB_SSLMODE}"
        return base

    @computed_field
    @property
    def COOKIE_SECURE(self) -> bool:
        return not self.DEBUG

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
