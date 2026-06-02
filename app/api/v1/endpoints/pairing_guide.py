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
from app.models.sake import Sake, SakanaCategory, Sakana
from app.models.user import User

router = APIRouter()


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
        "heroImage": item.hero_image,
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
    # Seasonal: items from the single featured category (admin-designated)
    featured_cat = session.exec(
        select(PairingCategory).where(PairingCategory.is_featured.is_(True))
    ).first()

    if featured_cat:
        seasonal_items = session.exec(
            select(PairingItem)
            .where(
                PairingItem.category_id == featured_cat.id,
                PairingItem.is_draft.is_(False),
            )
            .order_by(PairingItem.position.asc())
            .limit(3)
        ).all()
        seasonal = _resolve_many(session, seasonal_items)
        seasonal_label = featured_cat.label
    else:
        seasonal = []
        seasonal_label = ""

    # Classic: season=="通年" items only, no padding
    classic_items = session.exec(
        select(PairingItem)
        .where(
            PairingItem.season == "通年",
            PairingItem.is_draft.is_(False),
        )
        .order_by(PairingItem.position.asc())
        .limit(4)
    ).all()
    classic = _resolve_many(session, classic_items)

    sakana_cats = session.exec(
        select(SakanaCategory).order_by(SakanaCategory.position.asc())
    ).all()

    featured_sake = _featured_sake(session, viewer)
    return {
        "seasonal": {
            "label": seasonal_label,
            "items": [_home_card(*t) for t in seasonal],
        },
        "classic": {
            "items": [_home_card(*t) for t in classic],
        },
        "foodCategories": [
            {"key": c.slug, "label": c.label} for c in sakana_cats
        ],
        "featuredSake": _serialize_featured(*featured_sake) if featured_sake else None,
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

    return {"categories": out_categories}


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
