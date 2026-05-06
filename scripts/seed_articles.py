"""Seed article and article_category from the legacy ARTICLES dict.

Idempotent on slug. Re-running upserts category and articles by slug.

Usage:
    docker compose exec backend uv run python scripts/seed_articles.py
"""
import sys
from datetime import date as Date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlmodel import Session, select

from app.core.article_seed_data import ARTICLES, CATEGORY_FILTERS
from app.core.database import engine
from app.models.article import Article, ArticleCategory


def seed() -> dict[str, int]:
    cat_inserted = cat_updated = 0
    art_inserted = art_updated = 0
    with Session(engine) as session:
        # Skip "all" — it's a virtual filter, not a category
        real_cats = [c for c in CATEGORY_FILTERS if c["key"] != "all"]
        for pos, cat in enumerate(real_cats):
            existing = session.exec(
                select(ArticleCategory).where(ArticleCategory.slug == cat["key"])
            ).first()
            if existing:
                existing.label = cat["label"]
                existing.position = pos
                session.add(existing)
                cat_updated += 1
            else:
                session.add(
                    ArticleCategory(
                        slug=cat["key"], label=cat["label"], position=pos
                    )
                )
                cat_inserted += 1
        session.commit()

        # Resolve slug → id
        cat_map = {
            c.slug: c.id
            for c in session.exec(select(ArticleCategory)).all()
        }

        for art in ARTICLES:
            cat_id = cat_map.get(art["category"])
            if cat_id is None:
                raise SystemExit(
                    f"Article {art['slug']!r} references unknown category {art['category']!r}"
                )
            existing = session.exec(
                select(Article).where(Article.slug == art["slug"])
            ).first()
            fields = {
                "title": art["title"],
                "subtitle": art["subtitle"],
                "excerpt": art["excerpt"],
                "category_id": cat_id,
                "date": Date.fromisoformat(art["date"]),
                "read_time": art["readTime"],
                "emoji": art["emoji"],
                "hero_image_url": None,
                "body": art["body"],
                "updated_at": datetime.utcnow(),
            }
            if existing:
                for k, v in fields.items():
                    setattr(existing, k, v)
                session.add(existing)
                art_updated += 1
            else:
                session.add(Article(slug=art["slug"], **fields))
                art_inserted += 1

        session.commit()

    return {
        "cat_inserted": cat_inserted,
        "cat_updated": cat_updated,
        "art_inserted": art_inserted,
        "art_updated": art_updated,
    }


def main() -> None:
    s = seed()
    print(f"category: inserted={s['cat_inserted']} updated={s['cat_updated']}")
    print(f"article:  inserted={s['art_inserted']} updated={s['art_updated']}")


if __name__ == "__main__":
    main()
