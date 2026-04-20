import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class JournalEntry(SQLModel, table=True):
    __tablename__ = "journal_entry"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    user_id: int = Field(foreign_key="user.id", index=True)
    sake_name: str
    brewery: str | None = None
    category: str | None = None
    date: str
    rating: int
    image_path: str | None = None
    tasting: dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False))
    created_at: datetime = Field(default_factory=datetime.utcnow)
