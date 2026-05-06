"""Pairing guide endpoints — joins pairing_item with sake + sakana.

Items reference Sake (sake_id) and Sakana (sakana_id) as required FKs,
so display data (food name, sake name, images) is always derived from
the canonical entities. Admin UI manages these via /api/v1/admin/pairings.
"""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.deps import get_optional_user
from app.core.database import get_session
from app.models.pairing_guide import PairingCategory, PairingItem
from app.models.sake import Sake, Sakana
from app.models.user import User

router = APIRouter()

SEASON_FILTERS = [
    {"key": "all", "label": "すべて"},
    {"key": "your-type", "label": "あなたのタイプ"},
    {"key": "winter", "label": "冬", "match": "冬"},
    {"key": "year-round", "label": "通年", "match": "通年"},
]


def _summary(item: PairingItem, sake: Sake, sakana: Sakana) -> dict:
    return {
        "id": item.id,
        "emoji": sakana.emoji,
        "foodName": sakana.name,
        "sakeName": sake.name,
        "sakeBrewery": sake.brewery,
        "sakeType": sake.type,
        "temperature": item.temperature,
        "season": item.season,
        "description": item.description,
        "foodImage": sakana.food_image_url,
        "sakeImage": sake.image_url,
        "heroImage": item.hero_image,
    }


def _detail(item: PairingItem, sake: Sake, sakana: Sakana) -> dict:
    return {
        **_summary(item, sake, sakana),
        "body": item.body,
        "whyItWorks": item.why_it_works,
        "howToEnjoy": item.how_to_enjoy,
        "bodyHtml": item.body_html,
    }


def _home_card(item: PairingItem, sake: Sake, sakana: Sakana) -> dict:
    return {
        "id": item.id,
        "emoji": sakana.emoji,
        "food": sakana.name,
        "sake": sake.name,
        "temperature": item.temperature,
        "description": item.description,
    }


def _resolve_one(
    session: Session, item: PairingItem
) -> tuple[PairingItem, Sake, Sakana] | None:
    sake = session.get(Sake, item.sake_id)
    sakana = session.get(Sakana, item.sakana_id)
    if not sake or not sakana:
        return None
    return item, sake, sakana


def _resolve_many(
    session: Session, items: list[PairingItem]
) -> list[tuple[PairingItem, Sake, Sakana]]:
    out = []
    for it in items:
        triple = _resolve_one(session, it)
        if triple:
            out.append(triple)
    return out


def _persona_axis_score(persona_code: str, sake: Sake) -> int:
    """How many of the 4 persona axes this sake matches (0-4)."""
    score = 0
    code = persona_code.upper()
    if len(code) < 4:
        return score
    # S/D — sweet vs dry
    if (code[0] == "S") == (sake.sweetness >= 0.5):
        score += 1
    # H/E — heavy/full vs easy/light-bodied (using umami as body proxy)
    if (code[1] == "H") == (sake.umami >= 0.5):
        score += 1
    # R/L — rich/aromatic vs light/restrained
    if (code[2] == "R") == (sake.aroma >= 0.5):
        score += 1
    # B/S — bold/grippy vs smooth (using bitterness)
    if (code[3] == "B") == (sake.bitterness >= 0.5):
        score += 1
    return score


def _featured_sake(
    session: Session, viewer: User | None
) -> tuple[Sake, bool] | None:
    """Pick today's recommended sake.

    Hybrid strategy:
      1. If the viewer is signed in with a persona, score each sake by axis
         alignment and keep only the top scorers, then rotate within that pool
         using (date + user_id) as the seed.
      2. Otherwise rotate across all sakes using today's date as the seed.

    Returns (sake, personalized) or None when the catalog is empty.
    """
    sakes = session.exec(select(Sake).order_by(Sake.id.asc())).all()
    if not sakes:
        return None

    today_seed = date.today().toordinal()

    if viewer and viewer.persona_code:
        scored = [(s, _persona_axis_score(viewer.persona_code, s)) for s in sakes]
        max_score = max(score for _, score in scored)
        if max_score > 0:
            top = [s for s, score in scored if score == max_score]
            seed = (today_seed + (viewer.id or 0)) % len(top)
            return top[seed], True

    return sakes[today_seed % len(sakes)], False


def _serialize_featured(sake: Sake, personalized: bool) -> dict:
    return {
        "id": sake.id,
        "name": sake.name,
        "brewery": sake.brewery,
        "region": sake.region,
        "type": sake.type,
        "description": sake.description,
        "imageUrl": sake.image_url,
        "personalized": personalized,
    }


@router.get("/home")
def get_home(
    session: Session = Depends(get_session),
    viewer: User | None = Depends(get_optional_user),
):
    items = session.exec(
        select(PairingItem)
        .where(PairingItem.is_draft.is_(False))
        .order_by(PairingItem.position.asc())
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

    featured = _featured_sake(session, viewer)
    return {
        "seasonal": {
            "label": "WINTER COLLECTION",
            "items": [_home_card(*t) for t in seasonal],
        },
        "classic": {
            "items": [_home_card(*t) for t in classic],
        },
        "foodCategories": [{"key": c.slug, "label": c.label} for c in cats],
        "featuredSake": _serialize_featured(*featured) if featured else None,
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
            .where(
                PairingItem.category_id == cat.id,
                PairingItem.is_draft.is_(False),
            )
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
            .where(
                PairingItem.category_id == cat.id,
                PairingItem.is_draft.is_(False),
            )
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
    if not item or item.is_draft:
        raise HTTPException(
            status_code=404, detail=f"Pairing item '{item_id}' not found"
        )
    triple = _resolve_one(session, item)
    if not triple:
        raise HTTPException(
            status_code=500,
            detail=f"Pairing item '{item_id}' references missing sake/sakana",
        )
    return _detail(*triple)
