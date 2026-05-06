from datetime import date, datetime

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    # Nullable so OAuth-only identities can exist alongside password ones.
    hashed_password: str | None = None
    is_admin: bool = Field(default=False)

    # Required for adult-content compliance (sake). Nullable in DB to keep
    # legacy rows compatible; the API enforces non-null on new signups.
    birthdate: date | None = None
    terms_accepted_at: datetime | None = None
    privacy_accepted_at: datetime | None = None

    # Profile
    display_name: str | None = None
    bio: str | None = None
    avatar_url: str | None = None

    # Persisted diagnosis result, e.g. "SHRB"
    persona_code: str | None = Field(default=None, index=True, max_length=4)

    password_changed_at: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
