"""Admin file upload endpoint — currently a stub.

Returns a placeholder response so the frontend BlockNote integration can wire up
its `uploadFile` callback today. The real implementation will hand back an S3
presigned PUT URL once the bucket and IAM are provisioned.
"""
import os
import re
import uuid
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.api.deps import require_admin

router = APIRouter(
    prefix="/admin/uploads",
    tags=["admin-uploads"],
    dependencies=[Depends(require_admin)],
)


SAFE_NAME_RE = re.compile(r"[^a-zA-Z0-9._-]+")
ALLOWED_PREFIXES = {"articles", "pairings", "sakana", "sake", "journal"}


class SignRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=200)
    content_type: str = Field(min_length=1, max_length=100)
    prefix: str = Field(default="articles", min_length=1, max_length=40)


class SignResponse(BaseModel):
    upload_url: str
    public_url: str
    key: str
    method: str = "PUT"
    headers: dict[str, str] = Field(default_factory=dict)
    expires_in: int = 3600
    stub: bool = True


def _safe_filename(name: str) -> str:
    base = SAFE_NAME_RE.sub("-", name).strip("-")
    return base or "file"


@router.post("/sign", response_model=SignResponse)
def sign_upload(body: SignRequest) -> SignResponse:
    prefix = body.prefix if body.prefix in ALLOWED_PREFIXES else "articles"
    safe = _safe_filename(body.filename)
    key = f"{prefix}/{uuid.uuid4()}-{safe}"

    bucket = os.environ.get("S3_BUCKET")
    public_base = os.environ.get(
        "S3_PUBLIC_BASE_URL",
        f"https://{bucket}.s3.amazonaws.com" if bucket else "https://example-cdn.local",
    )

    return SignResponse(
        upload_url=f"{public_base}/{key}?stub=1",
        public_url=f"{public_base}/{key}",
        key=key,
        headers={"Content-Type": body.content_type},
        stub=True,
    )
