"""Bootstrap an admin user from environment variables.

Idempotent. Reads ADMIN_EMAIL/ADMIN_USERNAME/ADMIN_PASSWORD; silently skips if
ADMIN_EMAIL is unset. Creates the user if missing, promotes if existing but not
admin. Never overwrites an existing password.

Usage:
    uv run python scripts/create_admin.py
"""
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlmodel import Session, select

from app.core.database import engine
from app.core.security import hash_password
from app.models.user import User


def bootstrap_admin() -> None:
    email = os.environ.get("ADMIN_EMAIL")
    username = os.environ.get("ADMIN_USERNAME")
    password = os.environ.get("ADMIN_PASSWORD")

    if not email:
        print("[create_admin] ADMIN_EMAIL not set, skipping.")
        return

    if not username or not password:
        print(
            "[create_admin] ADMIN_EMAIL is set but ADMIN_USERNAME or "
            "ADMIN_PASSWORD is missing — skipping.",
            file=sys.stderr,
        )
        return

    with Session(engine) as session:
        existing = session.exec(select(User).where(User.email == email)).first()
        if existing:
            if not existing.is_admin:
                existing.is_admin = True
                session.add(existing)
                session.commit()
                print(f"[create_admin] Promoted existing user {email} to admin.")
            else:
                print(f"[create_admin] Admin {email} already exists.")
            return

        now = datetime.utcnow()
        user = User(
            email=email,
            username=username,
            hashed_password=hash_password(password),
            is_admin=True,
            terms_accepted_at=now,
            privacy_accepted_at=now,
            password_changed_at=now,
        )
        session.add(user)
        session.commit()
        print(f"[create_admin] Created admin user {email}.")


if __name__ == "__main__":
    bootstrap_admin()
