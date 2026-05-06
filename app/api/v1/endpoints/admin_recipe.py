"""Admin CRUD for Recipe (dish + cooking instructions)."""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.api.deps import require_admin
from app.core.database import get_session
from app.models.sake import Recipe, SakeRecipe

router = APIRouter(
    prefix="/admin/recipes",
    tags=["admin-recipe"],
    dependencies=[Depends(require_admin)],
)


class IngredientInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    amount: str = Field(min_length=1, max_length=50)


class RecipeInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    emoji: str = Field(min_length=1, max_length=10)
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


def _serialize(r: Recipe) -> dict[str, Any]:
    return {
        "id": r.id,
        "name": r.name,
        "emoji": r.emoji,
        "imagePlaceholder": r.image_placeholder,
        "foodImageUrl": r.food_image_url,
        "sweetness": r.sweetness,
        "umami": r.umami,
        "acidity": r.acidity,
        "fat": r.fat,
        "aroma": r.aroma,
        "saltiness": r.saltiness,
        "ingredients": r.ingredients or [],
        "steps": r.steps or [],
        "prepTimeMin": r.prep_time_min,
        "cookTimeMin": r.cook_time_min,
        "servings": r.servings,
        "difficulty": r.difficulty,
    }


@router.get("")
def list_recipes(session: Session = Depends(get_session)) -> list[dict]:
    rows = session.exec(select(Recipe).order_by(Recipe.name.asc())).all()
    return [_serialize(r) for r in rows]


@router.get("/{recipe_id}")
def get_recipe(recipe_id: str, session: Session = Depends(get_session)) -> dict:
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return _serialize(recipe)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_recipe(
    body: RecipeInput, session: Session = Depends(get_session)
) -> dict:
    if session.exec(select(Recipe).where(Recipe.name == body.name)).first():
        raise HTTPException(status_code=409, detail="Recipe name already exists")
    recipe = Recipe(
        **body.model_dump(exclude={"ingredients"}),
        ingredients=[i.model_dump() for i in body.ingredients]
        if body.ingredients
        else None,
    )
    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return _serialize(recipe)


@router.put("/{recipe_id}")
def update_recipe(
    recipe_id: str,
    body: RecipeInput,
    session: Session = Depends(get_session),
) -> dict:
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    if recipe.name != body.name:
        clash = session.exec(
            select(Recipe).where(Recipe.name == body.name, Recipe.id != recipe_id)
        ).first()
        if clash:
            raise HTTPException(status_code=409, detail="Recipe name already exists")
    data = body.model_dump(exclude={"ingredients"})
    for k, v in data.items():
        setattr(recipe, k, v)
    recipe.ingredients = (
        [i.model_dump() for i in body.ingredients] if body.ingredients else None
    )
    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return _serialize(recipe)


@router.delete("/{recipe_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recipe(recipe_id: str, session: Session = Depends(get_session)) -> None:
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    pairing_count = len(
        session.exec(
            select(SakeRecipe).where(SakeRecipe.recipe_id == recipe_id)
        ).all()
    )
    if pairing_count > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Recipe is referenced by {pairing_count} sake pairing(s); remove those first",
        )
    session.delete(recipe)
    session.commit()
