"""Admin data export / import — full JSON snapshot of every content table.

Lets an admin pull a single JSON containing every row across all 12 application
tables (users, journal entries, sake catalog, sakana, articles, pairings, etc.)
for offline backup, and restore that file to recreate or augment a database.

Import is upsert by primary key — running the same payload twice is safe.
Tables are imported in FK-dependency order so foreign keys resolve cleanly.
"""
from datetime import date, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, SQLModel, select

from app.api.deps import require_admin
from app.core.database import get_session
from app.models.article import Article, ArticleCategory
from app.models.event import Event
from app.models.journal import JournalEntry
from app.models.pairing_guide import PairingCategory, PairingItem
from app.models.sake import Flavor, Sake, SakeFlavor, SakeSakana, Sakana
from app.models.user import User

router = APIRouter(
    prefix="/admin/data",
    tags=["admin-data"],
    dependencies=[Depends(require_admin)],
)


# Order matters for FK resolution. Children come after parents on import; the
# inverse order is used when deleting in `replace` mode.
EXPORT_ORDER: list[tuple[str, type[SQLModel]]] = [
    ("user", User),
    ("flavor", Flavor),
    ("event", Event),
    ("article_category", ArticleCategory),
    ("pairing_category", PairingCategory),
    ("sake", Sake),
    ("sakana", Sakana),
    ("article", Article),
    ("pairing_item", PairingItem),
    ("sake_flavor", SakeFlavor),
    ("sake_sakana", SakeSakana),
    ("journal_entry", JournalEntry),
]

EXPORT_VERSION = 1


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {k: _to_jsonable(v) for k, v in value.items()}
    return value


def _row_to_dict(row: SQLModel) -> dict[str, Any]:
    return {k: _to_jsonable(v) for k, v in row.model_dump().items()}


@router.get("/export")
def export_all(session: Session = Depends(get_session)) -> dict[str, Any]:
    tables: dict[str, list[dict[str, Any]]] = {}
    counts: dict[str, int] = {}
    for tbl_name, model in EXPORT_ORDER:
        rows = session.exec(select(model)).all()
        tables[tbl_name] = [_row_to_dict(r) for r in rows]
        counts[tbl_name] = len(rows)
    return {
        "version": EXPORT_VERSION,
        "exported_at": datetime.utcnow().isoformat(),
        "counts": counts,
        "tables": tables,
    }


class ImportRequest(BaseModel):
    version: int
    tables: dict[str, list[dict[str, Any]]]
    # Future-proofing fields are accepted but unused.
    exported_at: str | None = None
    counts: dict[str, int] | None = None


def _pk_values(model: type[SQLModel], row: dict[str, Any]) -> dict[str, Any]:
    pk_cols = [c.name for c in model.__table__.primary_key.columns]
    out: dict[str, Any] = {}
    for col in pk_cols:
        if col not in row:
            raise HTTPException(
                status_code=400,
                detail=f"Row in '{model.__tablename__}' missing primary key '{col}'",
            )
        out[col] = row[col]
    return out


@router.post("/import")
def import_all(
    body: ImportRequest, session: Session = Depends(get_session)
) -> dict[str, Any]:
    if body.version != EXPORT_VERSION:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported export version {body.version}; expected {EXPORT_VERSION}",
        )

    inserted: dict[str, int] = {}
    updated: dict[str, int] = {}

    for tbl_name, model in EXPORT_ORDER:
        rows = body.tables.get(tbl_name, [])
        ins = upd = 0
        for raw in rows:
            pk = _pk_values(model, raw)
            existing = session.exec(select(model).filter_by(**pk)).first()
            if existing is not None:
                for key, value in raw.items():
                    if key in pk:
                        continue
                    setattr(existing, key, value)
                session.add(existing)
                upd += 1
            else:
                obj = model(**raw)
                session.add(obj)
                ins += 1
        session.commit()
        inserted[tbl_name] = ins
        updated[tbl_name] = upd

    return {
        "version": EXPORT_VERSION,
        "imported_at": datetime.utcnow().isoformat(),
        "inserted": inserted,
        "updated": updated,
    }
