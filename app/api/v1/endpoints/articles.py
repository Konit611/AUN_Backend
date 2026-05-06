"""Articles (yomimono) endpoints — reads from article / article_category tables.

Seed via scripts/seed_articles.py. Admin manages content via /api/v1/admin/articles.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.api.v1.schemas import paginate
from app.core.database import get_session
from app.models.article import Article, ArticleCategory

router = APIRouter()

VIRTUAL_ALL_FILTER = {"key": "all", "label": "すべて"}


def _serialize_summary(article: Article, category: ArticleCategory) -> dict:
    return {
        "slug": article.slug,
        "title": article.title,
        "subtitle": article.subtitle,
        "category": category.slug,
        "categoryLabel": category.label,
        "date": article.date.isoformat(),
        "readTime": article.read_time,
        "emoji": article.emoji,
        "heroImageUrl": article.hero_image_url,
        "excerpt": article.excerpt,
    }


def _serialize_detail(article: Article, category: ArticleCategory) -> dict:
    return {**_serialize_summary(article, category), "body": article.body}


def _category_filters(session: Session) -> list[dict]:
    cats = session.exec(
        select(ArticleCategory).order_by(ArticleCategory.position.asc())
    ).all()
    return [VIRTUAL_ALL_FILTER] + [
        {"key": c.slug, "label": c.label} for c in cats
    ]


@router.get("/articles")
def list_articles(
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
    session: Session = Depends(get_session),
):
    cats = session.exec(select(ArticleCategory)).all()
    cat_by_id = {c.id: c for c in cats}

    if category and category != "all":
        cat = next((c for c in cats if c.slug == category), None)
        if not cat:
            articles: list[Article] = []
        else:
            articles = session.exec(
                select(Article)
                .where(Article.category_id == cat.id)
                .order_by(Article.date.desc())
            ).all()
    else:
        articles = session.exec(
            select(Article).order_by(Article.date.desc())
        ).all()

    items = [_serialize_summary(a, cat_by_id[a.category_id]) for a in articles]
    result = paginate(items, page, page_size)
    result["filters"] = {"categories": _category_filters(session)}
    return result


@router.get("/articles/{slug}")
def get_article(slug: str, session: Session = Depends(get_session)):
    article = session.exec(select(Article).where(Article.slug == slug)).first()
    if not article:
        raise HTTPException(
            status_code=404, detail=f"Article with slug '{slug}' not found"
        )
    category = session.get(ArticleCategory, article.category_id)
    if not category:
        raise HTTPException(
            status_code=500,
            detail=f"Article '{slug}' references missing category",
        )
    return _serialize_detail(article, category)
