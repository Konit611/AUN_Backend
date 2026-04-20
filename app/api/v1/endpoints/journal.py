import math
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy import func
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.core.database import get_session
from app.models.journal import JournalEntry
from app.models.user import User

router = APIRouter()


class SakeProfile(BaseModel):
    sweetDry: int
    heavyLight: int
    richCalm: int
    boldSmooth: int


class TastingNote(BaseModel):
    profile: SakeProfile
    aroma: str
    taste: str
    finish: str
    temperature: str
    pairing: Optional[str] = None
    memo: Optional[str] = None


class JournalEntryCreate(BaseModel):
    sakeName: str
    brewery: Optional[str] = None
    category: Optional[str] = None
    date: str
    rating: int
    tasting: TastingNote
    imagePath: Optional[str] = None


def _serialize(entry: JournalEntry) -> dict:
    return {
        "id": entry.id,
        "sakeName": entry.sake_name,
        "brewery": entry.brewery,
        "category": entry.category,
        "date": entry.date,
        "rating": entry.rating,
        "tasting": entry.tasting,
        "imagePath": entry.image_path,
    }


@router.get("/journal")
def list_entries(
    page: int = 1,
    page_size: int = 20,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    total = session.exec(
        select(func.count(JournalEntry.id)).where(
            JournalEntry.user_id == current_user.id
        )
    ).one()
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    page = max(1, min(page, total_pages))
    entries = session.exec(
        select(JournalEntry)
        .where(JournalEntry.user_id == current_user.id)
        .order_by(JournalEntry.date.desc(), JournalEntry.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return {
        "items": [_serialize(e) for e in entries],
        "total": total,
        "page": page,
        "pageSize": page_size,
        "totalPages": total_pages,
    }


@router.get("/journal/{entry_id}")
def get_entry(
    entry_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    entry = session.get(JournalEntry, entry_id)
    if not entry or entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Journal entry '{entry_id}' not found",
        )
    return _serialize(entry)


@router.post("/journal", status_code=status.HTTP_201_CREATED)
def create_entry(
    body: JournalEntryCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    entry = JournalEntry(
        user_id=current_user.id,
        sake_name=body.sakeName,
        brewery=body.brewery,
        category=body.category,
        date=body.date,
        rating=body.rating,
        image_path=body.imagePath,
        tasting=body.tasting.model_dump(),
    )
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return _serialize(entry)


@router.put("/journal/{entry_id}")
def update_entry(
    entry_id: str,
    body: JournalEntryCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    entry = session.get(JournalEntry, entry_id)
    if not entry or entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Journal entry '{entry_id}' not found",
        )
    entry.sake_name = body.sakeName
    entry.brewery = body.brewery
    entry.category = body.category
    entry.date = body.date
    entry.rating = body.rating
    entry.image_path = body.imagePath
    entry.tasting = body.tasting.model_dump()
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return _serialize(entry)


@router.delete("/journal/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(
    entry_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    entry = session.get(JournalEntry, entry_id)
    if not entry or entry.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Journal entry '{entry_id}' not found",
        )
    session.delete(entry)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
