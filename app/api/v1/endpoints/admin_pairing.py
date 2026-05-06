"""Admin CRUD for PairingItem (curated pairing-guide entries) and PairingCategory."""
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.api.deps import require_admin
from app.core.database import get_session
from app.models.pairing_guide import PairingCategory, PairingItem
from app.models.sake import Recipe, Sake

router = APIRouter(
    prefix="/admin",
    tags=["admin-pairing"],
    dependencies=[Depends(require_admin)],
)


class CategoryInput(BaseModel):
    slug: str = Field(min_length=1, max_length=40, pattern=r"^[a-z0-9-]+$")
    label: str = Field(min_length=1, max_length=40)
    title: str = Field(min_length=1, max_length=80)
    position: int = 0


class PairingItemInput(BaseModel):
    id: str | None = None
    category_id: int
    sake_id: str = Field(min_length=1)
    recipe_id: str = Field(min_length=1)
    temperature: str = Field(min_length=1)
    season: str = Field(min_length=1)
    description: str = Field(min_length=1)
    body: str = Field(min_length=1)
    why_it_works: str = Field(min_length=1)
    how_to_enjoy: str = Field(min_length=1)
    hero_image: str | None = None
    persona_code: str | None = None
    position: int = 0


def _serialize_category(c: PairingCategory) -> dict[str, Any]:
    return {
        "id": c.id,
        "slug": c.slug,
        "label": c.label,
        "title": c.title,
        "position": c.position,
    }


def _serialize_item(
    item: PairingItem, sake: Sake, recipe: Recipe
) -> dict[str, Any]:
    return {
        "id": item.id,
        "categoryId": item.category_id,
        "sakeId": sake.id,
        "sakeName": sake.name,
        "sakeBrewery": sake.brewery,
        "sakeType": sake.type,
        "sakeImageUrl": sake.image_url,
        "recipeId": recipe.id,
        "recipeName": recipe.name,
        "recipeEmoji": recipe.emoji,
        "recipeImageUrl": recipe.food_image_url,
        "temperature": item.temperature,
        "season": item.season,
        "description": item.description,
        "body": item.body,
        "whyItWorks": item.why_it_works,
        "howToEnjoy": item.how_to_enjoy,
        "heroImage": item.hero_image,
        "personaCode": item.persona_code,
        "position": item.position,
    }


def _resolve(session: Session, item: PairingItem) -> dict[str, Any]:
    sake = session.get(Sake, item.sake_id)
    recipe = session.get(Recipe, item.recipe_id)
    if not sake or not recipe:
        raise HTTPException(
            status_code=500,
            detail=f"Pairing {item.id} references missing sake/recipe",
        )
    return _serialize_item(item, sake, recipe)


# ── Categories ────────────────────────────────────


@router.get("/pairing-categories")
def list_categories(session: Session = Depends(get_session)) -> list[dict]:
    rows = session.exec(
        select(PairingCategory).order_by(PairingCategory.position.asc())
    ).all()
    return [_serialize_category(c) for c in rows]


@router.post("/pairing-categories", status_code=status.HTTP_201_CREATED)
def create_category(
    body: CategoryInput, session: Session = Depends(get_session)
) -> dict:
    if session.exec(
        select(PairingCategory).where(PairingCategory.slug == body.slug)
    ).first():
        raise HTTPException(status_code=409, detail="Slug already exists")
    cat = PairingCategory(**body.model_dump())
    session.add(cat)
    session.commit()
    session.refresh(cat)
    return _serialize_category(cat)


@router.put("/pairing-categories/{category_id}")
def update_category(
    category_id: int,
    body: CategoryInput,
    session: Session = Depends(get_session),
) -> dict:
    cat = session.get(PairingCategory, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    if cat.slug != body.slug:
        clash = session.exec(
            select(PairingCategory).where(
                PairingCategory.slug == body.slug,
                PairingCategory.id != category_id,
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


@router.delete("/pairing-categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int, session: Session = Depends(get_session)
) -> None:
    cat = session.get(PairingCategory, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    item_count = len(
        session.exec(
            select(PairingItem).where(PairingItem.category_id == category_id)
        ).all()
    )
    if item_count > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Category has {item_count} item(s); remove or reassign first",
        )
    session.delete(cat)
    session.commit()


# ── Pairing items ─────────────────────────────────


@router.get("/pairings")
def list_pairings(session: Session = Depends(get_session)) -> list[dict]:
    rows = session.exec(
        select(PairingItem).order_by(
            PairingItem.category_id.asc(), PairingItem.position.asc()
        )
    ).all()
    return [_resolve(session, i) for i in rows]


@router.get("/pairings/{item_id}")
def get_pairing(item_id: str, session: Session = Depends(get_session)) -> dict:
    item = session.get(PairingItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Pairing not found")
    return _resolve(session, item)


def _validate_refs(session: Session, body: PairingItemInput) -> None:
    if not session.get(PairingCategory, body.category_id):
        raise HTTPException(status_code=400, detail="Unknown category_id")
    if not session.get(Sake, body.sake_id):
        raise HTTPException(status_code=400, detail="Unknown sake_id")
    if not session.get(Recipe, body.recipe_id):
        raise HTTPException(status_code=400, detail="Unknown recipe_id")


@router.post("/pairings", status_code=status.HTTP_201_CREATED)
def create_pairing(
    body: PairingItemInput, session: Session = Depends(get_session)
) -> dict:
    _validate_refs(session, body)
    item_id = body.id or str(uuid.uuid4())
    if session.get(PairingItem, item_id):
        raise HTTPException(status_code=409, detail="Pairing id already exists")
    data = body.model_dump(exclude={"id"})
    item = PairingItem(id=item_id, **data)
    session.add(item)
    session.commit()
    session.refresh(item)
    return _resolve(session, item)


@router.put("/pairings/{item_id}")
def update_pairing(
    item_id: str,
    body: PairingItemInput,
    session: Session = Depends(get_session),
) -> dict:
    item = session.get(PairingItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Pairing not found")
    _validate_refs(session, body)
    data = body.model_dump(exclude={"id"})
    for k, v in data.items():
        setattr(item, k, v)
    session.add(item)
    session.commit()
    session.refresh(item)
    return _resolve(session, item)


@router.delete("/pairings/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pairing(item_id: str, session: Session = Depends(get_session)) -> None:
    item = session.get(PairingItem, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Pairing not found")
    session.delete(item)
    session.commit()
