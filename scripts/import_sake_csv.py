"""Import sake data from normalized CSV files into the database.

Usage (inside the backend container):
    docker compose exec backend uv run python scripts/import_sake_csv.py

Reads five CSVs from `aun_back/data/`:
    - sake.csv          (one row per sake; no flavor/pairing columns)
    - flavor.csv        (master: id, label)
    - sakana.csv        (master: id, name, emoji, image_placeholder)
    - sake_flavor.csv   (M2M: sake_id, flavor_id, is_primary, position)
    - sake_sakana.csv   (M2M: sake_id, sakana_id, description, position)

Behaviour:
    - Idempotent on primary keys. Existing rows are updated; new rows inserted.
    - Join tables (sake_flavor / sake_sakana) are fully replaced per sake_id
      that appears in those CSVs — children are recreated from the CSV.
    - Rows present in DB but missing from the CSVs are NOT deleted.

CSV columns:
    sake.csv:        id, name, brewery, region, description, type, rice,
                     polishing, serving_temperature, serving_season, persona_code
    flavor.csv:      id, label
    sakana.csv:      id, name, emoji, image_placeholder,
                     sweetness, umami, acidity, fat, aroma, saltiness
    sake_flavor.csv: sake_id, flavor_id, is_primary, position
    sake_sakana.csv: sake_id, sakana_id, description, position
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlmodel import Session, delete

from app.core.database import engine
from app.models.sake import Flavor, Sake, SakeFlavor, SakeSakana, Sakana


DATA_DIR = Path(__file__).resolve().parent.parent / "data"

SAKE_REQUIRED = {
    "id", "name", "brewery", "region", "description", "type", "rice",
    "polishing", "serving_temperature", "serving_season",
    "sweetness", "umami", "acidity", "bitterness", "aroma",
}
FLAVOR_REQUIRED = {"id", "label"}
SAKANA_REQUIRED = {
    "id", "name", "emoji",
    "sweetness", "umami", "acidity", "fat", "aroma", "saltiness",
}
SAKE_FLAVOR_REQUIRED = {"sake_id", "flavor_id", "is_primary", "position"}
SAKE_SAKANA_REQUIRED = {"sake_id", "sakana_id", "description", "position"}


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"true", "1", "yes", "y"}


def _clean(value: str | None) -> str:
    return (value or "").strip()


def _optional(value: str | None) -> str | None:
    cleaned = _clean(value)
    return cleaned or None


def _read_csv(path: Path, required: set[str]) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"CSV not found: {path}")
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = set(reader.fieldnames or [])
        missing = required - fields
        if missing:
            raise SystemExit(
                f"{path.name} missing required columns: {sorted(missing)}\n"
                f"Found columns: {sorted(fields)}"
            )
        return list(reader)


def _upsert_sake(session: Session, rows: list[dict]) -> tuple[int, int]:
    inserted = updated = 0
    for line_no, row in enumerate(rows, start=2):
        sake_id = _clean(row.get("id"))
        if not sake_id:
            continue
        missing = [c for c in SAKE_REQUIRED if not _clean(row.get(c))]
        if missing:
            raise SystemExit(
                f"sake.csv row {line_no} (id={sake_id!r}) missing: {missing}"
            )
        axes = {
            "sweetness": float(_clean(row["sweetness"])),
            "umami": float(_clean(row["umami"])),
            "acidity": float(_clean(row["acidity"])),
            "bitterness": float(_clean(row["bitterness"])),
            "aroma": float(_clean(row["aroma"])),
        }
        existing = session.get(Sake, sake_id)
        if existing:
            existing.name = _clean(row["name"])
            existing.brewery = _clean(row["brewery"])
            existing.region = _clean(row["region"])
            existing.description = _clean(row["description"])
            existing.type = _clean(row["type"])
            existing.rice = _clean(row["rice"])
            existing.polishing = _clean(row["polishing"])
            existing.serving_temperature = _clean(row["serving_temperature"])
            existing.serving_season = _clean(row["serving_season"])
            for k, v in axes.items():
                setattr(existing, k, v)
            session.add(existing)
            updated += 1
        else:
            session.add(Sake(
                id=sake_id,
                name=_clean(row["name"]),
                brewery=_clean(row["brewery"]),
                region=_clean(row["region"]),
                description=_clean(row["description"]),
                type=_clean(row["type"]),
                rice=_clean(row["rice"]),
                polishing=_clean(row["polishing"]),
                serving_temperature=_clean(row["serving_temperature"]),
                serving_season=_clean(row["serving_season"]),
                **axes,
            ))
            inserted += 1
    return inserted, updated


def _upsert_flavor(session: Session, rows: list[dict]) -> tuple[int, int]:
    inserted = updated = 0
    for line_no, row in enumerate(rows, start=2):
        fid = _clean(row.get("id"))
        label = _clean(row.get("label"))
        if not fid or not label:
            raise SystemExit(f"flavor.csv row {line_no} missing id/label")
        existing = session.get(Flavor, fid)
        if existing:
            existing.label = label
            session.add(existing)
            updated += 1
        else:
            session.add(Flavor(id=fid, label=label))
            inserted += 1
    return inserted, updated


SAKANA_AXES = ("sweetness", "umami", "acidity", "fat", "aroma", "saltiness")


def _upsert_sakana(session: Session, rows: list[dict]) -> tuple[int, int]:
    inserted = updated = 0
    for line_no, row in enumerate(rows, start=2):
        sid = _clean(row.get("id"))
        name = _clean(row.get("name"))
        emoji = _clean(row.get("emoji"))
        if not sid or not name or not emoji:
            raise SystemExit(
                f"sakana.csv row {line_no} missing id/name/emoji"
            )
        try:
            axes = {a: float(_clean(row[a])) for a in SAKANA_AXES}
        except (KeyError, ValueError) as e:
            raise SystemExit(
                f"sakana.csv row {line_no} (id={sid!r}) invalid axis value: {e}"
            )
        image = _optional(row.get("image_placeholder"))
        existing = session.get(Sakana, sid)
        if existing:
            existing.name = name
            existing.emoji = emoji
            existing.image_placeholder = image
            for k, v in axes.items():
                setattr(existing, k, v)
            session.add(existing)
            updated += 1
        else:
            session.add(Sakana(
                id=sid, name=name, emoji=emoji, image_placeholder=image,
                **axes,
            ))
            inserted += 1
    return inserted, updated


def _replace_join(
    session: Session,
    rows: list[dict],
    model,
    sake_key: str,
    other_key: str,
    build_row,
    csv_name: str,
) -> int:
    sake_ids = {_clean(r.get(sake_key)) for r in rows if _clean(r.get(sake_key))}
    for sid in sake_ids:
        session.exec(delete(model).where(getattr(model, sake_key) == sid))
    session.flush()

    count = 0
    for line_no, row in enumerate(rows, start=2):
        sid = _clean(row.get(sake_key))
        oid = _clean(row.get(other_key))
        if not sid or not oid:
            raise SystemExit(
                f"{csv_name} row {line_no} missing {sake_key}/{other_key}"
            )
        session.add(build_row(row))
        count += 1
    return count


def import_all() -> dict[str, tuple[int, int] | int]:
    sake_rows = _read_csv(DATA_DIR / "sake.csv", SAKE_REQUIRED)
    flavor_rows = _read_csv(DATA_DIR / "flavor.csv", FLAVOR_REQUIRED)
    sakana_rows = _read_csv(DATA_DIR / "sakana.csv", SAKANA_REQUIRED)
    sake_flavor_rows = _read_csv(
        DATA_DIR / "sake_flavor.csv", SAKE_FLAVOR_REQUIRED
    )
    sake_sakana_rows = _read_csv(
        DATA_DIR / "sake_sakana.csv", SAKE_SAKANA_REQUIRED
    )

    with Session(engine) as session:
        sake_stats = _upsert_sake(session, sake_rows)
        flavor_stats = _upsert_flavor(session, flavor_rows)
        sakana_stats = _upsert_sakana(session, sakana_rows)
        session.flush()

        sf_count = _replace_join(
            session, sake_flavor_rows, SakeFlavor, "sake_id", "flavor_id",
            lambda r: SakeFlavor(
                sake_id=_clean(r["sake_id"]),
                flavor_id=_clean(r["flavor_id"]),
                is_primary=_truthy(r.get("is_primary")),
                position=int(_clean(r.get("position")) or 0),
            ),
            "sake_flavor.csv",
        )
        ss_count = _replace_join(
            session, sake_sakana_rows, SakeSakana, "sake_id", "sakana_id",
            lambda r: SakeSakana(
                sake_id=_clean(r["sake_id"]),
                sakana_id=_clean(r["sakana_id"]),
                description=_clean(r.get("description")),
                position=int(_clean(r.get("position")) or 0),
            ),
            "sake_sakana.csv",
        )
        session.commit()

    return {
        "sake": sake_stats,
        "flavor": flavor_stats,
        "sakana": sakana_stats,
        "sake_flavor": sf_count,
        "sake_sakana": ss_count,
    }


def main() -> None:
    stats = import_all()
    print(f"sake:        inserted={stats['sake'][0]} updated={stats['sake'][1]}")
    print(f"flavor:      inserted={stats['flavor'][0]} updated={stats['flavor'][1]}")
    print(f"sakana:      inserted={stats['sakana'][0]} updated={stats['sakana'][1]}")
    print(f"sake_flavor: rebuilt={stats['sake_flavor']}")
    print(f"sake_sakana: rebuilt={stats['sake_sakana']}")


if __name__ == "__main__":
    main()
