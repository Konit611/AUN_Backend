from datetime import date, datetime
from typing import Any

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class ArticleCategory(SQLModel, table=True):
    __tablename__ = "article_category"

    id: int | None = Field(default=None, primary_key=True)
    slug: str = Field(unique=True, index=True)
    label: str
    position: int = 0


class Article(SQLModel, table=True):
    __tablename__ = "article"

    id: int | None = Field(default=None, primary_key=True)
    slug: str = Field(unique=True, index=True)
    title: str
    subtitle: str
    excerpt: str
    category_id: int = Field(foreign_key="article_category.id", index=True)
    date: date
    read_time: str
    emoji: str
    hero_image_url: str | None = None
    # Legacy block-array body (paragraph/heading/image/quote). Kept for back-compat
    # with rows authored before the BlockNote editor migration.
    body: list[dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    # BlockNote editor state (PartialBlock[]) — source of truth for new entries.
    body_json: list[dict[str, Any]] | None = Field(
        default=None, sa_column=Column(JSON, nullable=True)
    )
    # Pre-rendered HTML used by SSR for SEO. Set when body_json is saved.
    body_html: str | None = None
    is_draft: bool = Field(default=False, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
