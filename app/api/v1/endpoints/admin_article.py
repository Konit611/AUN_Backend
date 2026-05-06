"""Admin CRUD for Article and ArticleCategory (yomimono)."""
from datetime import date as Date, datetime
from typing import Any, Literal, Union

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.api.deps import require_admin
from app.core.database import get_session
from app.models.article import Article, ArticleCategory

router = APIRouter(
    prefix="/admin",
    tags=["admin-article"],
    dependencies=[Depends(require_admin)],
)


# ── Block schemas ─────────────────────────────────


class ParagraphBlock(BaseModel):
    type: Literal["paragraph"]
    text: str = Field(min_length=1)


class HeadingBlock(BaseModel):
    type: Literal["heading"]
    text: str = Field(min_length=1)


class ImageBlock(BaseModel):
    type: Literal["image"]
    emoji: str = Field(min_length=1, max_length=10)
    caption: str = Field(min_length=1)
    image_url: str | None = None


class QuoteBlock(BaseModel):
    type: Literal["quote"]
    text: str = Field(min_length=1)
    author: str = Field(min_length=1)


Block = Union[ParagraphBlock, HeadingBlock, ImageBlock, QuoteBlock]


# ── Categories ────────────────────────────────────


class CategoryInput(BaseModel):
    slug: str = Field(min_length=1, max_length=40, pattern=r"^[a-z0-9-]+$")
    label: str = Field(min_length=1, max_length=60)
    position: int = 0


def _serialize_category(c: ArticleCategory) -> dict[str, Any]:
    return {
        "id": c.id,
        "slug": c.slug,
        "label": c.label,
        "position": c.position,
    }


@router.get("/article-categories")
def list_categories(session: Session = Depends(get_session)) -> list[dict]:
    rows = session.exec(
        select(ArticleCategory).order_by(ArticleCategory.position.asc())
    ).all()
    return [_serialize_category(c) for c in rows]


@router.post("/article-categories", status_code=status.HTTP_201_CREATED)
def create_category(
    body: CategoryInput, session: Session = Depends(get_session)
) -> dict:
    if session.exec(
        select(ArticleCategory).where(ArticleCategory.slug == body.slug)
    ).first():
        raise HTTPException(status_code=409, detail="Slug already exists")
    cat = ArticleCategory(**body.model_dump())
    session.add(cat)
    session.commit()
    session.refresh(cat)
    return _serialize_category(cat)


@router.put("/article-categories/{category_id}")
def update_category(
    category_id: int,
    body: CategoryInput,
    session: Session = Depends(get_session),
) -> dict:
    cat = session.get(ArticleCategory, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    if cat.slug != body.slug:
        clash = session.exec(
            select(ArticleCategory).where(
                ArticleCategory.slug == body.slug,
                ArticleCategory.id != category_id,
            )
        ).first()
        if clash:
            raise HTTPException(status_code=409, detail="Slug already exists")
    for k, v in body.model_dump().items():
        setattr(cat, k, v)
    session.add(cat)
    session.commit()
    session.refresh(cat)
    return _serialize_category(cat)


@router.delete(
    "/article-categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_category(
    category_id: int, session: Session = Depends(get_session)
) -> None:
    cat = session.get(ArticleCategory, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    article_count = len(
        session.exec(
            select(Article).where(Article.category_id == category_id)
        ).all()
    )
    if article_count > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Category has {article_count} article(s); reassign or delete first",
        )
    session.delete(cat)
    session.commit()


# ── Articles ──────────────────────────────────────


class ArticleInput(BaseModel):
    # Drafts loosen most validations; published entries enforce them.
    slug: str = Field(min_length=1, max_length=80, pattern=r"^[a-z0-9-]+$")
    title: str = Field(min_length=1, max_length=120)
    subtitle: str = ""
    excerpt: str = ""
    category_id: int
    date: Date
    read_time: str = ""
    emoji: str = ""
    hero_image_url: str | None = None
    body: list[Block] = Field(default_factory=list)
    body_json: list[dict[str, Any]] | None = None
    body_html: str | None = None
    is_draft: bool = False


def _serialize_article(a: Article, c: ArticleCategory) -> dict[str, Any]:
    return {
        "id": a.id,
        "slug": a.slug,
        "title": a.title,
        "subtitle": a.subtitle,
        "excerpt": a.excerpt,
        "categoryId": c.id,
        "categorySlug": c.slug,
        "categoryLabel": c.label,
        "date": a.date.isoformat(),
        "readTime": a.read_time,
        "emoji": a.emoji,
        "heroImageUrl": a.hero_image_url,
        "body": a.body,
        "bodyJson": a.body_json,
        "bodyHtml": a.body_html,
        "isDraft": a.is_draft,
        "updatedAt": a.updated_at.isoformat() if a.updated_at else None,
    }


@router.get("/articles")
def list_articles(session: Session = Depends(get_session)) -> list[dict]:
    cats = {c.id: c for c in session.exec(select(ArticleCategory)).all()}
    rows = session.exec(select(Article).order_by(Article.date.desc())).all()
    out = []
    for a in rows:
        cat = cats.get(a.category_id)
        if cat:
            out.append(_serialize_article(a, cat))
    return out


@router.get("/articles/{slug}")
def get_article(slug: str, session: Session = Depends(get_session)) -> dict:
    article = session.exec(select(Article).where(Article.slug == slug)).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    cat = session.get(ArticleCategory, article.category_id)
    if not cat:
        raise HTTPException(status_code=500, detail="Article references missing category")
    return _serialize_article(article, cat)


def _enforce_publish_rules(body: ArticleInput) -> None:
    if body.is_draft:
        return
    missing = [
        k for k, v in {
            "subtitle": body.subtitle,
            "excerpt": body.excerpt,
            "read_time": body.read_time,
            "emoji": body.emoji,
        }.items() if not v
    ]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot publish without: {', '.join(missing)}",
        )


@router.post("/articles", status_code=status.HTTP_201_CREATED)
def create_article(
    body: ArticleInput, session: Session = Depends(get_session)
) -> dict:
    cat = session.get(ArticleCategory, body.category_id)
    if not cat:
        raise HTTPException(status_code=400, detail="Unknown category_id")
    if session.exec(select(Article).where(Article.slug == body.slug)).first():
        raise HTTPException(status_code=409, detail="Slug already exists")
    _enforce_publish_rules(body)
    data = body.model_dump()
    data["body"] = [b.model_dump(exclude_none=True) for b in body.body]
    article = Article(**data, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
    session.add(article)
    session.commit()
    session.refresh(article)
    return _serialize_article(article, cat)


@router.put("/articles/{slug}")
def update_article(
    slug: str,
    body: ArticleInput,
    session: Session = Depends(get_session),
) -> dict:
    article = session.exec(select(Article).where(Article.slug == slug)).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    cat = session.get(ArticleCategory, body.category_id)
    if not cat:
        raise HTTPException(status_code=400, detail="Unknown category_id")
    if article.slug != body.slug:
        clash = session.exec(
            select(Article).where(
                Article.slug == body.slug, Article.id != article.id
            )
        ).first()
        if clash:
            raise HTTPException(status_code=409, detail="Slug already exists")
    _enforce_publish_rules(body)
    data = body.model_dump()
    data["body"] = [b.model_dump(exclude_none=True) for b in body.body]
    for k, v in data.items():
        setattr(article, k, v)
    article.updated_at = datetime.utcnow()
    session.add(article)
    session.commit()
    session.refresh(article)
    return _serialize_article(article, cat)


@router.delete("/articles/{slug}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(slug: str, session: Session = Depends(get_session)) -> None:
    article = session.exec(select(Article).where(Article.slug == slug)).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    session.delete(article)
    session.commit()
