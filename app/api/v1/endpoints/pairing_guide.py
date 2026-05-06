"""Pairing guide endpoints — joins pairing_item with sake + recipe.

Items reference Sake (sake_id) and Recipe (recipe_id) as required FKs,
so display data (food name, sake name, images) is always derived from
the canonical entities. Admin UI manages these via /api/v1/admin/pairings.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.pairing_guide import PairingCategory, PairingItem
from app.models.sake import Recipe, Sake

router = APIRouter()

SEASON_FILTERS = [
    {"key": "all", "label": "すべて"},
    {"key": "your-type", "label": "あなたのタイプ"},
    {"key": "winter", "label": "冬", "match": "冬"},
    {"key": "year-round", "label": "通年", "match": "通年"},
]


def _summary(item: PairingItem, sake: Sake, recipe: Recipe) -> dict:
    return {
        "id": item.id,
        "emoji": recipe.emoji,
        "foodName": recipe.name,
        "sakeName": sake.name,
        "sakeBrewery": sake.brewery,
        "sakeType": sake.type,
        "temperature": item.temperature,
        "season": item.season,
        "description": item.description,
        "foodImage": recipe.food_image_url,
        "sakeImage": sake.image_url,
        "heroImage": item.hero_image,
    }


def _detail(item: PairingItem, sake: Sake, recipe: Recipe) -> dict:
    return {
        **_summary(item, sake, recipe),
        "body": item.body,
        "whyItWorks": item.why_it_works,
        "howToEnjoy": item.how_to_enjoy,
    }


def _home_card(item: PairingItem, sake: Sake, recipe: Recipe) -> dict:
    return {
        "id": item.id,
        "emoji": recipe.emoji,
        "food": recipe.name,
        "sake": sake.name,
        "temperature": item.temperature,
        "description": item.description,
    }


def _resolve_one(
    session: Session, item: PairingItem
) -> tuple[PairingItem, Sake, Recipe] | None:
    sake = session.get(Sake, item.sake_id)
    recipe = session.get(Recipe, item.recipe_id)
    if not sake or not recipe:
        return None
    return item, sake, recipe


def _resolve_many(
    session: Session, items: list[PairingItem]
) -> list[tuple[PairingItem, Sake, Recipe]]:
    out = []
    for it in items:
        triple = _resolve_one(session, it)
        if triple:
            out.append(triple)
    return out


@router.get("/home")
def get_home(session: Session = Depends(get_session)):
    items = session.exec(
        select(PairingItem).order_by(PairingItem.position.asc())
    ).all()
    resolved = _resolve_many(session, items)

    seasonal = [t for t in resolved if t[0].season == "冬"][:3]
    if len(seasonal) < 3:
        seasonal = resolved[:3]

    classic = [t for t in resolved if t[0].season == "通年"]
    if len(classic) < 4:
        seen = {t[0].id for t in classic}
        for t in resolved:
            if t[0].id not in seen:
                classic.append(t)
                if len(classic) >= 4:
                    break
    classic = classic[:4]

    cats = session.exec(
        select(PairingCategory).order_by(PairingCategory.position.asc())
    ).all()

    return {
        "seasonal": {
            "label": "WINTER COLLECTION",
            "items": [_home_card(*t) for t in seasonal],
        },
        "classic": {
            "items": [_home_card(*t) for t in classic],
        },
        "foodCategories": [{"key": c.slug, "label": c.label} for c in cats],
    }


@router.get("/pairing-guide")
def get_pairing_guide(session: Session = Depends(get_session)):
    cats = session.exec(
        select(PairingCategory).order_by(PairingCategory.position.asc())
    ).all()
    out_categories = []
    for cat in cats:
        items = session.exec(
            select(PairingItem)
            .where(PairingItem.category_id == cat.id)
            .order_by(PairingItem.position.asc())
        ).all()
        resolved = _resolve_many(session, items)
        out_categories.append({
            "slug": cat.slug,
            "label": cat.label,
            "title": cat.title,
            "items": [_summary(*t) for t in resolved],
        })

    food_filters = [{"key": c.slug, "label": c.label} for c in cats]
    return {
        "categories": out_categories,
        "filters": {
            "seasons": SEASON_FILTERS,
            "foodCategories": food_filters,
        },
    }


@router.get("/pairing-guide/categories")
def get_categories(session: Session = Depends(get_session)):
    cats = session.exec(
        select(PairingCategory).order_by(PairingCategory.position.asc())
    ).all()
    out = []
    for cat in cats:
        items = session.exec(
            select(PairingItem)
            .where(PairingItem.category_id == cat.id)
            .order_by(PairingItem.position.asc())
        ).all()
        resolved = _resolve_many(session, items)
        out.append({
            "slug": cat.slug,
            "label": cat.label,
            "title": cat.title,
            "items": [_summary(*t) for t in resolved],
        })
    return out


@router.get("/pairing-guide/items/{item_id}")
def get_item(item_id: str, session: Session = Depends(get_session)):
    item = session.get(PairingItem, item_id)
    if not item:
        raise HTTPException(
            status_code=404, detail=f"Pairing item '{item_id}' not found"
        )
    triple = _resolve_one(session, item)
    if not triple:
        raise HTTPException(
            status_code=500,
            detail=f"Pairing item '{item_id}' references missing sake/recipe",
        )
    return _detail(*triple)
