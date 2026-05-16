"""Admin CRUD for Sakana (肴 — dish + cooking instructions paired with sake)."""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.api.deps import require_admin
from app.core.database import get_session
from app.models.sake import Sakana, SakanaCategory, SakeSakana

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
    category_id: int
    # Emoji is a placeholder for when there's no food image — purely optional.
    emoji: str = Field(default="", max_length=10)
    description: str | None = None
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
        "categoryId": s.category_id,
        "emoji": s.emoji,
        "description": s.description,
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


# ── Categories ────────────────────────────────────


class CategoryInput(BaseModel):
    slug: str = Field(min_length=1, max_length=40, pattern=r"^[a-z0-9-]+$")
    label: str = Field(min_length=1, max_length=40)
    position: int = 0


def _serialize_category(c: SakanaCategory) -> dict[str, Any]:
    return {
        "id": c.id,
        "slug": c.slug,
        "label": c.label,
        "position": c.position,
    }


# Mounted on a separate path because the parent router prefix is /admin/sakana;
# we want categories under /admin/sakana-categories (matching pairing-categories).
category_router = APIRouter(
    prefix="/admin/sakana-categories",
    tags=["admin-sakana"],
    dependencies=[Depends(require_admin)],
)


@category_router.get("")
def list_categories(session: Session = Depends(get_session)) -> list[dict]:
    rows = session.exec(
        select(SakanaCategory).order_by(SakanaCategory.position.asc())
    ).all()
    return [_serialize_category(c) for c in rows]


@category_router.post("", status_code=status.HTTP_201_CREATED)
def create_category(
    body: CategoryInput, session: Session = Depends(get_session)
) -> dict:
    if session.exec(
        select(SakanaCategory).where(SakanaCategory.slug == body.slug)
    ).first():
        raise HTTPException(status_code=409, detail="Slug already exists")
    cat = SakanaCategory(**body.model_dump())
    session.add(cat)
    session.commit()
    session.refresh(cat)
    return _serialize_category(cat)


@category_router.put("/{category_id}")
def update_category(
    category_id: int,
    body: CategoryInput,
    session: Session = Depends(get_session),
) -> dict:
    cat = session.get(SakanaCategory, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    if cat.slug != body.slug:
        clash = session.exec(
            select(SakanaCategory).where(
                SakanaCategory.slug == body.slug,
                SakanaCategory.id != category_id,
            )
        ).first()
        if clash:
            raise HTTPException(status_code=409, detail="Slug already exists")
    for k, v in body.model_dump().items():
        setattr(cat, k, v)
    session.add(cat)
    session.commit()
    session.refresh(cat)
    return _serialize_category(cat)


@category_router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int, session: Session = Depends(get_session)
) -> None:
    cat = session.get(SakanaCategory, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    in_use = len(
        session.exec(
            select(Sakana).where(Sakana.category_id == category_id)
        ).all()
    )
    if in_use > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Category has {in_use} sakana; reassign first",
        )
    session.delete(cat)
    session.commit()
