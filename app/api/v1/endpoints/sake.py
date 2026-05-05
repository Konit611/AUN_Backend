from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.v1.schemas import paginate
from app.core.database import get_session
from app.models.sake import Flavor, Recipe, Sake, SakeFlavor, SakeRecipe

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
    flavor_rows: list[tuple[SakeFlavor, Flavor]],
    pairing_rows: list[tuple[SakeRecipe, Recipe]],
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
            {"label": flavor.label, "primary": link.is_primary}
            for link, flavor in flavor_rows
        ],
        "servingTags": _serving_tags(sake),
        "pairings": [
            {
                "emoji": recipe.emoji,
                "foodName": recipe.name,
                "description": link.description,
                "imagePlaceholder": recipe.image_placeholder or "",
            }
            for link, recipe in pairing_rows
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

    flavor_rows = session.exec(
        select(SakeFlavor, Flavor)
        .join(Flavor, SakeFlavor.flavor_id == Flavor.id)
        .where(SakeFlavor.sake_id == sake_id)
        .order_by(SakeFlavor.position.asc())
    ).all()
    pairing_rows = session.exec(
        select(SakeRecipe, Recipe)
        .join(Recipe, SakeRecipe.recipe_id == Recipe.id)
        .where(SakeRecipe.sake_id == sake_id)
        .order_by(SakeRecipe.position.asc())
    ).all()
    return _serialize_detail(sake, flavor_rows, pairing_rows)
