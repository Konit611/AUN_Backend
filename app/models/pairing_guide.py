from typing import Any

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class PairingCategory(SQLModel, table=True):
    __tablename__ = "pairing_category"

    id: int | None = Field(default=None, primary_key=True)
    slug: str = Field(unique=True, index=True)
    label: str
    title: str
    position: int = 0


class PairingItem(SQLModel, table=True):
    __tablename__ = "pairing_item"

    id: str = Field(primary_key=True)
    category_id: int = Field(foreign_key="pairing_category.id", index=True)
    # sake_id / sakana_id are nullable so drafts saved mid-wizard don't have to
    # commit to references yet. Publish path enforces non-null.
    sake_id: str | None = Field(default=None, foreign_key="sake.id", index=True)
    sakana_id: str | None = Field(default=None, foreign_key="sakana.id", index=True)
    temperature: str = ""
    season: str = ""
    description: str = ""
    # Legacy free-text fields. Authoring is unified under body_json/body_html via
    # the BlockNote editor; these stay nullable so old rows keep rendering.
    body: str | None = None
    why_it_works: str | None = None
    how_to_enjoy: str | None = None
    body_json: list[dict[str, Any]] | None = Field(
        default=None, sa_column=Column(JSON, nullable=True)
    )
    body_html: str | None = None
    is_draft: bool = Field(default=False, index=True)
    hero_image: str | None = None
    event_id: int | None = Field(default=None, foreign_key="event.id", index=True)
    persona_code: str | None = Field(default=None, index=True)
    position: int = 0
