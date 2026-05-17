"""Persona-coded quiz results.

For a 4-axis persona code (e.g. SHRB) we return:
  - top sakes ranked by taste-profile distance to that persona
  - curated PairingItems whose sake is among those top sakes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.persona_profile import distance, is_valid_code
from app.models.pairing_guide import PairingItem
from app.models.sake import Sake, Sakana

router = APIRouter()

TOP_SAKES = 3
MAX_PAIRINGS = 6


def _sake_tags(s: Sake) -> list[dict]:
    tags: list[dict] = []
    if s.serving_temperature:
        tags.append({"label": s.serving_temperature, "variant": "primary"})
    if s.serving_season:
        tags.append({"label": s.serving_season, "variant": "secondary"})
    return tags


@router.get("/quiz-results/{code}")
def get_quiz_result(code: str, session: Session = Depends(get_session)):
    code = code.upper()
    if not is_valid_code(code):
        raise HTTPException(
            status_code=400, detail=f"Invalid persona code: {code}"
        )

    all_sakes = session.exec(select(Sake)).all()
    top_sakes = sorted(all_sakes, key=lambda s: distance(s, code))[:TOP_SAKES]

    sakes = [
        {
            "id": s.id,
            "name": s.name,
            "brewery": s.brewery,
            "region": s.region,
            "description": s.description,
            "imageUrl": s.image_url,
            "tags": _sake_tags(s),
        }
        for s in top_sakes
    ]

    sake_ids = [s.id for s in top_sakes]
    pairing_items: list[PairingItem] = []
    if sake_ids:
        pairing_items = session.exec(
            select(PairingItem)
            .where(
                PairingItem.sake_id.in_(sake_ids),
                PairingItem.is_draft.is_(False),
            )
            .order_by(PairingItem.position.asc())
        ).all()

    pairings: list[dict] = []
    for item in pairing_items[:MAX_PAIRINGS]:
        sake = session.get(Sake, item.sake_id) if item.sake_id else None
        sakana = session.get(Sakana, item.sakana_id) if item.sakana_id else None
        if not sake or not sakana:
            continue
        pairings.append(
            {
                "id": item.id,
                "emoji": sakana.emoji,
                "foodName": sakana.name,
                "sakeName": sake.name,
                "temperature": item.temperature,
                "description": item.description,
                "foodImageUrl": sakana.food_image_url,
                "sakeImageUrl": sake.image_url,
            }
        )

    return {"sakes": sakes, "pairings": pairings}
