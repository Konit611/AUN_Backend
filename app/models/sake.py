import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class Sake(SQLModel, table=True):
    __tablename__ = "sake"

    id: str = Field(primary_key=True)
    name: str
    brewery: str
    region: str
    description: str
    type: str
    rice: str
    polishing: str
    serving_temperature: str
    serving_season: str
    sweetness: float = 0.5
    umami: float = 0.5
    acidity: float = 0.5
    bitterness: float = 0.3
    aroma: float = 0.5
    image_url: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Flavor(SQLModel, table=True):
    __tablename__ = "flavor"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    label: str = Field(unique=True, index=True)


class SakeFlavor(SQLModel, table=True):
    __tablename__ = "sake_flavor"

    sake_id: str = Field(foreign_key="sake.id", primary_key=True)
    flavor_id: str = Field(foreign_key="flavor.id", primary_key=True)
    is_primary: bool = False
    position: int = 0


class Sakana(SQLModel, table=True):
    __tablename__ = "sakana"

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        primary_key=True,
    )
    name: str = Field(unique=True, index=True)
    emoji: str
    image_placeholder: str | None = None
    sweetness: float = 0.5
    umami: float = 0.5
    acidity: float = 0.3
    fat: float = 0.3
    aroma: float = 0.4
    saltiness: float = 0.3
    food_image_url: str | None = None
    ingredients: list[dict[str, Any]] | None = Field(
        default=None, sa_column=Column(JSON)
    )
    steps: list[str] | None = Field(default=None, sa_column=Column(JSON))
    prep_time_min: int | None = None
    cook_time_min: int | None = None
    servings: int | None = None
    difficulty: str | None = None  # "easy" | "medium" | "hard"


class SakeSakana(SQLModel, table=True):
    __tablename__ = "sake_sakana"

    sake_id: str = Field(foreign_key="sake.id", primary_key=True)
    sakana_id: str = Field(foreign_key="sakana.id", primary_key=True)
    description: str
    position: int = 0
