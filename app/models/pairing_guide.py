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
    emoji: str
    food_name: str
    sake_name: str
    sake_brewery: str
    sake_type: str
    temperature: str
    season: str
    description: str
    body: str
    why_it_works: str
    how_to_enjoy: str
    food_image: str | None = None
    sake_image: str | None = None
    sake_id: str | None = Field(default=None, foreign_key="sake.id", index=True)
    event_id: int | None = Field(default=None, foreign_key="event.id", index=True)
    persona_code: str | None = Field(default=None, index=True)
    position: int = 0
