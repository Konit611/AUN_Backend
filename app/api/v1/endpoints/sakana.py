"""Public Sakana (肴) endpoints — list and detail.

A "sakana" is a dish curated for sake pairing. The public surface exposes:
  - GET /sakana          — paginated list with summary fields
  - GET /sakana/{id}     — full detail including ingredients, steps, and
                            sakes paired with this sakana
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.v1.schemas import paginate
from app.core.database import get_session
from app.core.pairing_score import rank_sakes
from app.models.sake import Sake, SakanaCategory, SakeSakana, Sakana

router = APIRouter()


def _summary(s: Sakana) -> dict:
    return {
        "id": s.id,
        "name": s.name,
        "categoryId": s.category_id,
        "emoji": s.emoji,
        "imagePlaceholder": s.image_placeholder,
        "foodImageUrl": s.food_image_url,
        "tasteAxes": {
            "sweetness": s.sweetness,
            "umami": s.umami,
            "acidity": s.acidity,
            "fat": s.fat,
            "aroma": s.aroma,
            "saltiness": s.saltiness,
        },
        "prepTimeMin": s.prep_time_min,
        "cookTimeMin": s.cook_time_min,
        "difficulty": s.difficulty,
    }


def _detail(
    s: Sakana,
    paired_sakes: list[tuple[SakeSakana, Sake]],
    suggested_sakes: list[Sake],
) -> dict:
    return {
        **_summary(s),
        "description": s.description,
        "ingredients": s.ingredients or [],
        "steps": s.steps or [],
        "servings": s.servings,
        "pairings": [
            {
                "sakeId": sake.id,
                "sakeName": sake.name,
                "brewery": sake.brewery,
                "region": sake.region,
                "type": sake.type,
                "imageUrl": sake.image_url,
                "description": link.description,
            }
            for link, sake in paired_sakes
        ],
        "synergyPairings": [
            {
                "sakeId": sake.id,
                "sakeName": sake.name,
                "brewery": sake.brewery,
                "type": sake.type,
                "imageUrl": sake.image_url,
            }
            for sake in suggested_sakes
        ],
    }


@router.get("/sakana")
def list_sakana(
    page: int = 1,
    page_size: int = 20,
    category: str | None = None,
    session: Session = Depends(get_session),
):
    stmt = select(Sakana).order_by(Sakana.name.asc())
    if category:
        cat = session.exec(
            select(SakanaCategory).where(SakanaCategory.slug == category)
        ).first()
        if not cat:
            return paginate([], page, page_size)
        stmt = stmt.where(Sakana.category_id == cat.id)
    rows = session.exec(stmt).all()
    items = [_summary(s) for s in rows]
    return paginate(items, page, page_size)


@router.get("/sakana-categories")
def list_sakana_categories(session: Session = Depends(get_session)) -> list[dict]:
    rows = session.exec(
        select(SakanaCategory).order_by(SakanaCategory.position.asc())
    ).all()
    return [
        {"id": c.id, "slug": c.slug, "label": c.label, "position": c.position}
        for c in rows
    ]


@router.get("/sakana/{sakana_id}")
def get_sakana(sakana_id: str, session: Session = Depends(get_session)):
    sakana = session.get(Sakana, sakana_id)
    if not sakana:
        raise HTTPException(
            status_code=404, detail=f"Sakana '{sakana_id}' not found"
        )

    paired = session.exec(
        select(SakeSakana, Sake)
        .join(Sake, SakeSakana.sake_id == Sake.id)
        .where(SakeSakana.sakana_id == sakana_id)
        .order_by(SakeSakana.position.asc())
    ).all()

    all_sakes = session.exec(select(Sake)).all()
    suggested = [s for s, _ in rank_sakes(sakana, all_sakes, "synergy", top_k=3)]

    return _detail(sakana, paired, suggested)
