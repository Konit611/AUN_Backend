"""Seed pairing_category from the legacy CATEGORIES dict.

After the FK refactor, pairing_item rows are created via the admin UI.
Only categories are bootstrapped here. Idempotent on slug.

Usage:
    docker compose exec backend uv run python scripts/seed_pairing_guide.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlmodel import Session, select

from app.core.database import engine
from app.core.pairing_seed_data import CATEGORIES
from app.models.pairing_guide import PairingCategory


def seed() -> dict[str, int]:
    inserted = updated = 0
    with Session(engine) as session:
        for pos, cat_data in enumerate(CATEGORIES):
            existing = session.exec(
                select(PairingCategory).where(PairingCategory.slug == cat_data["slug"])
            ).first()
            if existing:
                existing.label = cat_data["label"]
                existing.title = cat_data["title"]
                existing.position = pos
                session.add(existing)
                updated += 1
            else:
                session.add(
                    PairingCategory(
                        slug=cat_data["slug"],
                        label=cat_data["label"],
                        title=cat_data["title"],
                        position=pos,
                    )
                )
                inserted += 1
        session.commit()
    return {"inserted": inserted, "updated": updated}


def main() -> None:
    stats = seed()
    print(f"category: inserted={stats['inserted']} updated={stats['updated']}")
    print("Pairing items are managed via the admin UI (/admin/pairing).")


if __name__ == "__main__":
    main()
