from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.v1.schemas import paginate
from app.core.database import get_session
from app.core.pairing_score import rank_recipes
from app.core.persona_profile import distance, is_valid_code
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


def _serialize_pairing(recipe: Recipe, description: str = "") -> dict:
    return {
        "emoji": recipe.emoji,
        "foodName": recipe.name,
        "description": description,
        "imagePlaceholder": recipe.image_placeholder or "",
    }


def _serialize_detail(
    sake: Sake,
    flavor_rows: list[tuple[SakeFlavor, Flavor]],
    pairing_rows: list[tuple[SakeRecipe, Recipe]],
    all_recipes: list[Recipe],
) -> dict:
    def algo_pairings(mode: str) -> list[dict]:
        return [
            _serialize_pairing(r)
            for r, _score in rank_recipes(sake, all_recipes, mode, top_k=3)
        ]

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
            _serialize_pairing(recipe, link.description)
            for link, recipe in pairing_rows
        ],
        "synergyPairings": algo_pairings("synergy"),
        "cleansePairings": algo_pairings("cleanse"),
        "contrastPairings": algo_pairings("contrast"),
    }


@router.get("/sake")
def list_sake(
    page: int = 1,
    page_size: int = 20,
    persona: str | None = None,
    session: Session = Depends(get_session),
):
    if persona is not None:
        if not is_valid_code(persona):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid persona code '{persona}'. Expected 4 chars: [SD][HE][RL][BS].",
            )
        sakes = session.exec(select(Sake)).all()
        sakes = sorted(sakes, key=lambda s: distance(s, persona))
    else:
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
    all_recipes = session.exec(select(Recipe)).all()
    return _serialize_detail(sake, flavor_rows, pairing_rows, all_recipes)
