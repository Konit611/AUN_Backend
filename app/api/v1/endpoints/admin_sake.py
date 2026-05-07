"""Admin CRUD for Sake."""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select, delete

from app.api.deps import require_admin
from app.core.database import get_session
from app.models.sake import Flavor, Sake, SakeFlavor, SakeSakana, Sakana

router = APIRouter(
    prefix="/admin/sakes",
    tags=["admin-sake"],
    dependencies=[Depends(require_admin)],
)


class FlavorInput(BaseModel):
    flavor_id: str
    is_primary: bool = False


class PairingInput(BaseModel):
    sakana_id: str
    description: str = Field(min_length=1, max_length=500)
    position: int = 0


class SakeInput(BaseModel):
    id: str = Field(min_length=1, max_length=50, pattern=r"^[a-z0-9-]+$")
    name: str = Field(min_length=1, max_length=100)
    brewery: str = Field(min_length=1, max_length=100)
    region: str = Field(min_length=1, max_length=50)
    description: str
    type: str = Field(min_length=1, max_length=50)
    rice: str = Field(min_length=1, max_length=50)
    polishing: str = Field(min_length=1, max_length=20)
    serving_temperature: str
    serving_season: str
    sweetness: float = Field(ge=0.0, le=1.0)
    umami: float = Field(ge=0.0, le=1.0)
    acidity: float = Field(ge=0.0, le=1.0)
    bitterness: float = Field(ge=0.0, le=1.0)
    aroma: float = Field(ge=0.0, le=1.0)
    image_url: str | None = None
    purchase_url: str | None = None
    flavors: list[FlavorInput] = []
    pairings: list[PairingInput] = []


class SakeUpdateInput(BaseModel):
    """Like SakeInput but without id (id is path param)."""
    name: str = Field(min_length=1, max_length=100)
    brewery: str = Field(min_length=1, max_length=100)
    region: str = Field(min_length=1, max_length=50)
    description: str
    type: str = Field(min_length=1, max_length=50)
    rice: str = Field(min_length=1, max_length=50)
    polishing: str = Field(min_length=1, max_length=20)
    serving_temperature: str
    serving_season: str
    sweetness: float = Field(ge=0.0, le=1.0)
    umami: float = Field(ge=0.0, le=1.0)
    acidity: float = Field(ge=0.0, le=1.0)
    bitterness: float = Field(ge=0.0, le=1.0)
    aroma: float = Field(ge=0.0, le=1.0)
    image_url: str | None = None
    purchase_url: str | None = None
    flavors: list[FlavorInput] = []
    pairings: list[PairingInput] = []


def _serialize(
    sake: Sake,
    flavors: list[tuple[SakeFlavor, Flavor]],
    pairings: list[tuple[SakeSakana, Sakana]],
) -> dict[str, Any]:
    return {
        "id": sake.id,
        "name": sake.name,
        "brewery": sake.brewery,
        "region": sake.region,
        "description": sake.description,
        "type": sake.type,
        "rice": sake.rice,
        "polishing": sake.polishing,
        "servingTemperature": sake.serving_temperature,
        "servingSeason": sake.serving_season,
        "sweetness": sake.sweetness,
        "umami": sake.umami,
        "acidity": sake.acidity,
        "bitterness": sake.bitterness,
        "aroma": sake.aroma,
        "imageUrl": sake.image_url,
        "purchaseUrl": sake.purchase_url,
        "flavors": [
            {
                "flavorId": f.id,
                "label": f.label,
                "isPrimary": link.is_primary,
                "position": link.position,
            }
            for link, f in flavors
        ],
        "pairings": [
            {
                "sakanaId": s.id,
                "sakanaName": s.name,
                "emoji": s.emoji,
                "description": link.description,
                "position": link.position,
            }
            for link, s in pairings
        ],
    }


def _load_relations(session: Session, sake_id: str):
    flavors = session.exec(
        select(SakeFlavor, Flavor)
        .join(Flavor, SakeFlavor.flavor_id == Flavor.id)
        .where(SakeFlavor.sake_id == sake_id)
        .order_by(SakeFlavor.position.asc())
    ).all()
    pairings = session.exec(
        select(SakeSakana, Sakana)
        .join(Sakana, SakeSakana.sakana_id == Sakana.id)
        .where(SakeSakana.sake_id == sake_id)
        .order_by(SakeSakana.position.asc())
    ).all()
    return flavors, pairings


def _replace_relations(
    session: Session,
    sake_id: str,
    flavor_inputs: list[FlavorInput],
    pairing_inputs: list[PairingInput],
) -> None:
    session.exec(delete(SakeFlavor).where(SakeFlavor.sake_id == sake_id))
    session.exec(delete(SakeSakana).where(SakeSakana.sake_id == sake_id))
    session.flush()
    for i, f in enumerate(flavor_inputs):
        if not session.get(Flavor, f.flavor_id):
            raise HTTPException(
                status_code=400, detail=f"Unknown flavor_id: {f.flavor_id}"
            )
        session.add(
            SakeFlavor(
                sake_id=sake_id,
                flavor_id=f.flavor_id,
                is_primary=f.is_primary,
                position=i,
            )
        )
    for i, p in enumerate(pairing_inputs):
        if not session.get(Sakana, p.sakana_id):
            raise HTTPException(
                status_code=400, detail=f"Unknown sakana_id: {p.sakana_id}"
            )
        session.add(
            SakeSakana(
                sake_id=sake_id,
                sakana_id=p.sakana_id,
                description=p.description,
                position=p.position if p.position >= 0 else i,
            )
        )


@router.get("")
def list_sakes(session: Session = Depends(get_session)) -> list[dict]:
    rows = session.exec(select(Sake).order_by(Sake.created_at.asc())).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "brewery": s.brewery,
            "type": s.type,
            "imageUrl": s.image_url,
        }
        for s in rows
    ]


@router.get("/{sake_id}")
def get_sake(sake_id: str, session: Session = Depends(get_session)) -> dict:
    sake = session.get(Sake, sake_id)
    if not sake:
        raise HTTPException(status_code=404, detail="Sake not found")
    flavors, pairings = _load_relations(session, sake_id)
    return _serialize(sake, flavors, pairings)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_sake(body: SakeInput, session: Session = Depends(get_session)) -> dict:
    if session.get(Sake, body.id):
        raise HTTPException(status_code=409, detail="Sake id already exists")
    data = body.model_dump(exclude={"flavors", "pairings"})
    session.add(Sake(**data))
    session.flush()
    _replace_relations(session, body.id, body.flavors, body.pairings)
    session.commit()
    sake = session.get(Sake, body.id)
    flavors, pairings = _load_relations(session, body.id)
    return _serialize(sake, flavors, pairings)


@router.put("/{sake_id}")
def update_sake(
    sake_id: str,
    body: SakeUpdateInput,
    session: Session = Depends(get_session),
) -> dict:
    sake = session.get(Sake, sake_id)
    if not sake:
        raise HTTPException(status_code=404, detail="Sake not found")
    data = body.model_dump(exclude={"flavors", "pairings"})
    for k, v in data.items():
        setattr(sake, k, v)
    session.add(sake)
    session.flush()
    _replace_relations(session, sake_id, body.flavors, body.pairings)
    session.commit()
    session.refresh(sake)
    flavors, pairings = _load_relations(session, sake_id)
    return _serialize(sake, flavors, pairings)


@router.delete("/{sake_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sake(sake_id: str, session: Session = Depends(get_session)) -> None:
    sake = session.get(Sake, sake_id)
    if not sake:
        raise HTTPException(status_code=404, detail="Sake not found")
    session.exec(delete(SakeFlavor).where(SakeFlavor.sake_id == sake_id))
    session.exec(delete(SakeSakana).where(SakeSakana.sake_id == sake_id))
    session.delete(sake)
    session.commit()


@router.get("/_meta/flavors")
def list_flavors(session: Session = Depends(get_session)) -> list[dict]:
    rows = session.exec(select(Flavor).order_by(Flavor.label.asc())).all()
    return [{"id": f.id, "label": f.label} for f in rows]


@router.get("/_meta/sakana")
def list_sakana_for_pairing(
    session: Session = Depends(get_session),
) -> list[dict]:
    rows = session.exec(select(Sakana).order_by(Sakana.name.asc())).all()
    return [{"id": s.id, "name": s.name, "emoji": s.emoji} for s in rows]
