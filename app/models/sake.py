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
    persona_code: str | None = Field(default=None, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SakeFlavorTag(SQLModel, table=True):
    __tablename__ = "sake_flavor_tag"

    id: int | None = Field(default=None, primary_key=True)
    sake_id: str = Field(foreign_key="sake.id", index=True)
    label: str
    is_primary: bool = False
    position: int = 0


class SakePairing(SQLModel, table=True):
    __tablename__ = "sake_pairing"

    id: int | None = Field(default=None, primary_key=True)
    sake_id: str = Field(foreign_key="sake.id", index=True)
    emoji: str
    food_name: str
    description: str
    image_placeholder: str | None = None
    position: int = 0
