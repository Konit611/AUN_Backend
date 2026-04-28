from datetime import date, datetime

from sqlmodel import Field, SQLModel


class Event(SQLModel, table=True):
    """季節イベント / 시즌 기획 이벤트.

    User behavior tracking is a separate `analytics_event` table (Post-MVP).
    """

    __tablename__ = "event"

    id: int | None = Field(default=None, primary_key=True)
    name_ja: str
    description_ja: str | None = None
    start_date: date
    end_date: date
    created_at: datetime = Field(default_factory=datetime.utcnow)
