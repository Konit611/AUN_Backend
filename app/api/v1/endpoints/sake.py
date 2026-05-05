from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.v1.schemas import paginate
from app.core.database import get_session
from app.models.sake import Sake, SakeFlavorTag, SakePairing

router = APIRouter()


def _serving_tags(sake: Sake) -> list[str]:
    return [t for t in (sake.serving_temperature, sake.serving_season) if t]


def _serialize_summary(sake: Sake) -> dict:
    return {
        "id": sake.id,
        "name": sake.name,
        "brewery": sake.brewery,
        "region": sake.region,
        "servingTags": _serving_tags(sake),
    }


def _serialize_detail(
    sake: Sake,
    flavor_tags: list[SakeFlavorTag],
    pairings: list[SakePairing],
) -> dict:
    return {
        "id": sake.id,
        "name": sake.name,
        "brewery": sake.brewery,
        "region": sake.region,
        "description": sake.description,
        "type": sake.type,
        "rice": sake.rice,
        "polishing": sake.polishing,
        "flavorTags": [
            {"label": t.label, "primary": t.is_primary} for t in flavor_tags
        ],
        "servingTags": _serving_tags(sake),
        "pairings": [
            {
                "emoji": p.emoji,
                "foodName": p.food_name,
                "description": p.description,
                "imagePlaceholder": p.image_placeholder or "",
            }
            for p in pairings
        ],
    }


@router.get("/sake")
def list_sake(
    page: int = 1,
    page_size: int = 20,
    session: Session = Depends(get_session),
):
    sakes = session.exec(
        select(Sake).order_by(Sake.created_at.asc(), Sake.id.asc())
    ).all()
    items = [_serialize_summary(s) for s in sakes]
    return paginate(items, page, page_size)


@router.get("/sake/{sake_id}")
def get_sake(sake_id: str, session: Session = Depends(get_session)):
    sake = session.get(Sake, sake_id)
    if not sake:
        raise HTTPException(status_code=404, detail=f"Sake '{sake_id}' not found")

    flavor_tags = session.exec(
        select(SakeFlavorTag)
        .where(SakeFlavorTag.sake_id == sake_id)
        .order_by(SakeFlavorTag.position.asc())
    ).all()
    pairings = session.exec(
        select(SakePairing)
        .where(SakePairing.sake_id == sake_id)
        .order_by(SakePairing.position.asc())
    ).all()
    return _serialize_detail(sake, flavor_tags, pairings)
