"""Import sake data from a CSV spreadsheet into the database.

Usage (inside the backend container):
    docker compose exec backend uv run python scripts/import_sake_csv.py

Reads `aun_back/data/sake.csv` (one row per sake; wide format with
flavor_tags and pairings flattened across columns).

Behaviour:
    - Idempotent on `id`. Rows with an unchanged id replace the sake's
      flavor_tags and pairings (children are recreated from the CSV).
    - New ids are inserted.
    - Sakes present in DB but missing from the CSV are NOT deleted —
      drop them manually if needed.

CSV columns (see data/sake.csv for the canonical header):
    Required:   id, name, brewery, region, description, type, rice,
                polishing, serving_temperature, serving_season
    Optional:   persona_code
    Up to 4 flavor tags:
                flavor_{1..4}_label, flavor_{1..4}_primary  (TRUE/FALSE)
    Up to 3 pairings:
                pairing_{1..3}_emoji, pairing_{1..3}_food,
                pairing_{1..3}_description, pairing_{1..3}_image

Empty flavor/pairing slots are skipped.
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlmodel import Session, delete, select

from app.core.database import engine
from app.models.sake import Sake, SakeFlavorTag, SakePairing


CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "sake.csv"

REQUIRED_COLUMNS = {
    "id",
    "name",
    "brewery",
    "region",
    "description",
    "type",
    "rice",
    "polishing",
    "serving_temperature",
    "serving_season",
}


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"true", "1", "yes", "y"}


def _clean(value: str | None) -> str:
    return (value or "").strip()


def _optional(value: str | None) -> str | None:
    cleaned = _clean(value)
    return cleaned or None


def _extract_flavor_tags(row: dict, sake_id: str) -> list[SakeFlavorTag]:
    tags: list[SakeFlavorTag] = []
    for i in range(1, 5):
        label = _clean(row.get(f"flavor_{i}_label"))
        if not label:
            continue
        tags.append(
            SakeFlavorTag(
                sake_id=sake_id,
                label=label,
                is_primary=_truthy(row.get(f"flavor_{i}_primary")),
                position=i - 1,
            )
        )
    return tags


def _extract_pairings(row: dict, sake_id: str) -> list[SakePairing]:
    pairings: list[SakePairing] = []
    for i in range(1, 4):
        food = _clean(row.get(f"pairing_{i}_food"))
        if not food:
            continue
        pairings.append(
            SakePairing(
                sake_id=sake_id,
                emoji=_clean(row.get(f"pairing_{i}_emoji")),
                food_name=food,
                description=_clean(row.get(f"pairing_{i}_description")),
                image_placeholder=_optional(row.get(f"pairing_{i}_image")),
                position=i - 1,
            )
        )
    return pairings


def _validate_header(reader: csv.DictReader) -> None:
    fields = set(reader.fieldnames or [])
    missing = REQUIRED_COLUMNS - fields
    if missing:
        raise SystemExit(
            f"CSV is missing required columns: {sorted(missing)}\n"
            f"Found columns: {sorted(fields)}"
        )


def import_csv(csv_path: Path) -> tuple[int, int]:
    if not csv_path.exists():
        raise SystemExit(f"CSV not found: {csv_path}")

    inserted = 0
    updated = 0

    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        _validate_header(reader)

        with Session(engine) as session:
            for line_no, row in enumerate(reader, start=2):
                sake_id = _clean(row.get("id"))
                if not sake_id:
                    continue  # skip blank rows

                missing = [
                    col for col in REQUIRED_COLUMNS if not _clean(row.get(col))
                ]
                if missing:
                    raise SystemExit(
                        f"Row {line_no} (id={sake_id!r}) is missing values "
                        f"for required columns: {missing}"
                    )

                existing = session.get(Sake, sake_id)
                if existing:
                    # Update parent fields
                    existing.name = _clean(row["name"])
                    existing.brewery = _clean(row["brewery"])
                    existing.region = _clean(row["region"])
                    existing.description = _clean(row["description"])
                    existing.type = _clean(row["type"])
                    existing.rice = _clean(row["rice"])
                    existing.polishing = _clean(row["polishing"])
                    existing.serving_temperature = _clean(row["serving_temperature"])
                    existing.serving_season = _clean(row["serving_season"])
                    existing.persona_code = _optional(row.get("persona_code"))
                    session.add(existing)

                    # Replace children
                    session.exec(
                        delete(SakeFlavorTag).where(
                            SakeFlavorTag.sake_id == sake_id
                        )
                    )
                    session.exec(
                        delete(SakePairing).where(
                            SakePairing.sake_id == sake_id
                        )
                    )
                    updated += 1
                else:
                    sake = Sake(
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
                        persona_code=_optional(row.get("persona_code")),
                    )
                    session.add(sake)
                    inserted += 1

                for tag in _extract_flavor_tags(row, sake_id):
                    session.add(tag)
                for pairing in _extract_pairings(row, sake_id):
                    session.add(pairing)

            session.commit()

    return inserted, updated


def main() -> None:
    inserted, updated = import_csv(CSV_PATH)
    print(f"Imported sake from {CSV_PATH}: inserted={inserted} updated={updated}")


if __name__ == "__main__":
    main()
