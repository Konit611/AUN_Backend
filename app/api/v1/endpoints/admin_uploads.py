"""Admin file upload endpoint.

Issues short-lived presigned PUT URLs (S3-compatible: AWS S3, Supabase
Storage, R2, etc.) for the admin frontend's ImageUploader and BlockNote
editor. When STORAGE_* env vars are not configured the endpoint falls back
to a stub response so dev environments without storage keys keep working —
the frontend then inlines the file as a data URL.
"""
import os
import re
import uuid
from functools import lru_cache
from typing import Any

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.api.deps import require_admin

router = APIRouter(
    prefix="/admin/uploads",
    tags=["admin-uploads"],
    dependencies=[Depends(require_admin)],
)


SAFE_NAME_RE = re.compile(r"[^a-zA-Z0-9._-]+")
ALLOWED_PREFIXES = {"articles", "pairings", "sakana", "sake", "journal"}
PRESIGN_EXPIRES_SEC = 3600


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
    expires_in: int = PRESIGN_EXPIRES_SEC
    stub: bool = False


def _safe_filename(name: str) -> str:
    base = SAFE_NAME_RE.sub("-", name).strip("-")
    return base or "file"


def _s3_config() -> dict[str, Any] | None:
    """Return the storage config dict if env vars are fully set; else None (stub mode).

    Requires STORAGE_BUCKET, STORAGE_ENDPOINT_URL, and STORAGE_PUBLIC_BASE_URL
    to all be explicitly set. No provider-specific defaults are assumed.
    """
    bucket = os.environ.get("STORAGE_BUCKET")
    endpoint = os.environ.get("STORAGE_ENDPOINT_URL")
    public_base = os.environ.get("STORAGE_PUBLIC_BASE_URL")
    if not (bucket and endpoint and public_base):
        return None
    region = os.environ.get("STORAGE_REGION") or "us-east-1"
    return {
        "bucket": bucket,
        "region": region,
        "endpoint": endpoint,
        "public_base": public_base,
    }


@lru_cache(maxsize=1)
def _s3_client():
    """Boto3 S3-compatible client (works with any S3-compatible storage:
    Supabase Storage, Cloudflare R2, Backblaze B2, MinIO, etc.).

    Reads credentials from STORAGE_ACCESS_KEY_ID / STORAGE_SECRET_ACCESS_KEY
    and the endpoint from STORAGE_ENDPOINT_URL. Uses path-style addressing
    (required by Supabase Storage and most S3-compat providers).
    """
    cfg = _s3_config()
    if cfg is None:
        raise RuntimeError("Storage env vars not configured")
    return boto3.client(
        "s3",
        aws_access_key_id=os.environ.get("STORAGE_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("STORAGE_SECRET_ACCESS_KEY"),
        region_name=cfg["region"],
        endpoint_url=cfg["endpoint"],
        config=Config(
            signature_version="s3v4",
            s3={"addressing_style": "path"},
        ),
    )


def _stub_response(key: str, content_type: str) -> SignResponse:
    public_base = os.environ.get(
        "STORAGE_PUBLIC_BASE_URL", "https://example-cdn.local"
    )
    return SignResponse(
        upload_url=f"{public_base}/{key}?stub=1",
        public_url=f"{public_base}/{key}",
        key=key,
        headers={"Content-Type": content_type},
        stub=True,
    )


@router.post("/sign", response_model=SignResponse)
def sign_upload(body: SignRequest) -> SignResponse:
    prefix = body.prefix if body.prefix in ALLOWED_PREFIXES else "articles"
    key = f"{prefix}/{uuid.uuid4()}-{_safe_filename(body.filename)}"

    cfg = _s3_config()
    if cfg is None:
        return _stub_response(key, body.content_type)

    try:
        upload_url = _s3_client().generate_presigned_url(
            "put_object",
            Params={
                "Bucket": cfg["bucket"],
                "Key": key,
                "ContentType": body.content_type,
            },
            ExpiresIn=PRESIGN_EXPIRES_SEC,
            HttpMethod="PUT",
        )
    except (BotoCoreError, ClientError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to sign S3 URL: {e.__class__.__name__}",
        )

    return SignResponse(
        upload_url=upload_url,
        public_url=f"{cfg['public_base']}/{key}",
        key=key,
        headers={"Content-Type": body.content_type},
        stub=False,
    )
