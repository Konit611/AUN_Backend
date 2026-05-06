"""Admin CRUD for Sakana (肴 — dish + cooking instructions paired with sake)."""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.api.deps import require_admin
from app.core.database import get_session
from app.models.sake import Sakana, SakeSakana

router = APIRouter(
    prefix="/admin/sakana",
    tags=["admin-sakana"],
    dependencies=[Depends(require_admin)],
)


class IngredientInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    amount: str = Field(min_length=1, max_length=50)


class SakanaInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    emoji: str = Field(min_length=1, max_length=10)
    image_placeholder: str | None = None
    food_image_url: str | None = None
    sweetness: float = Field(ge=0.0, le=1.0)
    umami: float = Field(ge=0.0, le=1.0)
    acidity: float = Field(ge=0.0, le=1.0)
    fat: float = Field(ge=0.0, le=1.0)
    aroma: float = Field(ge=0.0, le=1.0)
    saltiness: float = Field(ge=0.0, le=1.0)
    ingredients: list[IngredientInput] | None = None
    steps: list[str] | None = None
    prep_time_min: int | None = Field(default=None, ge=0)
    cook_time_min: int | None = Field(default=None, ge=0)
    servings: int | None = Field(default=None, ge=1)
    difficulty: str | None = None


def _serialize(s: Sakana) -> dict[str, Any]:
    return {
        "id": s.id,
        "name": s.name,
        "emoji": s.emoji,
        "imagePlaceholder": s.image_placeholder,
        "foodImageUrl": s.food_image_url,
        "sweetness": s.sweetness,
        "umami": s.umami,
        "acidity": s.acidity,
        "fat": s.fat,
        "aroma": s.aroma,
        "saltiness": s.saltiness,
        "ingredients": s.ingredients or [],
        "steps": s.steps or [],
        "prepTimeMin": s.prep_time_min,
        "cookTimeMin": s.cook_time_min,
        "servings": s.servings,
        "difficulty": s.difficulty,
    }


@router.get("")
def list_sakana(session: Session = Depends(get_session)) -> list[dict]:
    rows = session.exec(select(Sakana).order_by(Sakana.name.asc())).all()
    return [_serialize(s) for s in rows]


@router.get("/{sakana_id}")
def get_sakana(sakana_id: str, session: Session = Depends(get_session)) -> dict:
    sakana = session.get(Sakana, sakana_id)
    if not sakana:
        raise HTTPException(status_code=404, detail="Sakana not found")
    return _serialize(sakana)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_sakana(
    body: SakanaInput, session: Session = Depends(get_session)
) -> dict:
    if session.exec(select(Sakana).where(Sakana.name == body.name)).first():
        raise HTTPException(status_code=409, detail="Sakana name already exists")
    sakana = Sakana(
        **body.model_dump(exclude={"ingredients"}),
        ingredients=[i.model_dump() for i in body.ingredients]
        if body.ingredients
        else None,
    )
    session.add(sakana)
    session.commit()
    session.refresh(sakana)
    return _serialize(sakana)


@router.put("/{sakana_id}")
def update_sakana(
    sakana_id: str,
    body: SakanaInput,
    session: Session = Depends(get_session),
) -> dict:
    sakana = session.get(Sakana, sakana_id)
    if not sakana:
        raise HTTPException(status_code=404, detail="Sakana not found")
    if sakana.name != body.name:
        clash = session.exec(
            select(Sakana).where(Sakana.name == body.name, Sakana.id != sakana_id)
        ).first()
        if clash:
            raise HTTPException(status_code=409, detail="Sakana name already exists")
    data = body.model_dump(exclude={"ingredients"})
    for k, v in data.items():
        setattr(sakana, k, v)
    sakana.ingredients = (
        [i.model_dump() for i in body.ingredients] if body.ingredients else None
    )
    session.add(sakana)
    session.commit()
    session.refresh(sakana)
    return _serialize(sakana)


@router.delete("/{sakana_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sakana(sakana_id: str, session: Session = Depends(get_session)) -> None:
    sakana = session.get(Sakana, sakana_id)
    if not sakana:
        raise HTTPException(status_code=404, detail="Sakana not found")
    pairing_count = len(
        session.exec(
            select(SakeSakana).where(SakeSakana.sakana_id == sakana_id)
        ).all()
    )
    if pairing_count > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Sakana is referenced by {pairing_count} sake pairing(s); remove those first",
        )
    session.delete(sakana)
    session.commit()
