import uuid
from datetime import datetime

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


class Recipe(SQLModel, table=True):
    __tablename__ = "recipe"

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


class SakeRecipe(SQLModel, table=True):
    __tablename__ = "sake_recipe"

    sake_id: str = Field(foreign_key="sake.id", primary_key=True)
    recipe_id: str = Field(foreign_key="recipe.id", primary_key=True)
    description: str
    position: int = 0
