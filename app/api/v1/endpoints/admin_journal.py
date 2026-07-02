"""Admin views over user journal entries.

Currently exposes an aggregation of off-catalog ("unverified") sakes — the
free-text names users recorded that aren't linked to the sake catalog. It is a
demand queue for deciding what to add to the catalog next; it does NOT touch the
sake table.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlmodel import Session, select

from app.api.deps import require_admin
from app.core.database import get_session
from app.models.journal import JournalEntry

router = APIRouter(
    prefix="/admin/journal",
    tags=["admin-journal"],
    dependencies=[Depends(require_admin)],
)


@router.get("/unverified-sakes")
def unverified_sakes(session: Session = Depends(get_session)) -> list[dict]:
    """Free-text sakes users logged that aren't linked to the catalog,
    grouped by name/brewery and ordered by how often they were recorded."""
    rows = session.exec(
        select(
            JournalEntry.sake_name,
            JournalEntry.brewery,
            func.count().label("count"),
        )
        .where(JournalEntry.sake_id.is_(None))
        .group_by(JournalEntry.sake_name, JournalEntry.brewery)
        .order_by(func.count().desc(), JournalEntry.sake_name.asc())
    ).all()
    return [
        {"sakeName": name, "brewery": brewery, "count": count}
        for name, brewery, count in rows
    ]
