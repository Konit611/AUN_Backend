from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_session
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


MIN_AGE_YEARS = 20
PERSONA_CODE_LEN = 4


def _years_old(birthdate: date, today: date | None = None) -> int:
    today = today or date.today()
    years = today.year - birthdate.year
    if (today.month, today.day) < (birthdate.month, birthdate.day):
        years -= 1
    return years


class SignupRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=2, max_length=32)
    password: str = Field(min_length=8, max_length=128)
    birthdate: date
    terms_accepted: bool
    privacy_accepted: bool
    persona_code: str | None = Field(default=None, min_length=PERSONA_CODE_LEN, max_length=PERSONA_CODE_LEN)

    @field_validator("terms_accepted")
    @classmethod
    def _terms_required(cls, v: bool) -> bool:
        if not v:
            raise ValueError("terms must be accepted")
        return v

    @field_validator("privacy_accepted")
    @classmethod
    def _privacy_required(cls, v: bool) -> bool:
        if not v:
            raise ValueError("privacy policy must be accepted")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ProfileUpdateRequest(BaseModel):
    display_name: str | None = Field(default=None, max_length=64)
    bio: str | None = Field(default=None, max_length=500)
    avatar_url: str | None = Field(default=None, max_length=500)
    persona_code: str | None = Field(default=None, min_length=PERSONA_CODE_LEN, max_length=PERSONA_CODE_LEN)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class UserPublic(BaseModel):
    id: int
    email: EmailStr
    username: str
    is_admin: bool
    birthdate: date | None
    display_name: str | None
    bio: str | None
    avatar_url: str | None
    persona_code: str | None
    has_password: bool
    created_at: datetime

    @classmethod
    def from_user(cls, user: User) -> "UserPublic":
        return cls(
            id=user.id,  # type: ignore[arg-type]
            email=user.email,
            username=user.username,
            is_admin=user.is_admin,
            birthdate=user.birthdate,
            display_name=user.display_name,
            bio=user.bio,
            avatar_url=user.avatar_url,
            persona_code=user.persona_code,
            has_password=user.hashed_password is not None,
            created_at=user.created_at,
        )


def _set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key=settings.AUTH_COOKIE_NAME,
        value=token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        path="/",
    )


@router.post("/signup", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def signup(
    body: SignupRequest,
    response: Response,
    session: Session = Depends(get_session),
) -> UserPublic:
    if _years_old(body.birthdate) < MIN_AGE_YEARS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Must be at least {MIN_AGE_YEARS} years old",
        )
    existing = session.exec(
        select(User).where((User.email == body.email) | (User.username == body.username))
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email or username already registered",
        )

    now = datetime.utcnow()
    user = User(
        email=body.email,
        username=body.username,
        hashed_password=hash_password(body.password),
        birthdate=body.birthdate,
        terms_accepted_at=now,
        privacy_accepted_at=now,
        persona_code=body.persona_code,
        password_changed_at=now,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    _set_auth_cookie(response, create_access_token(user.id))  # type: ignore[arg-type]
    return UserPublic.from_user(user)


@router.post("/login", response_model=UserPublic)
def login(
    body: LoginRequest,
    response: Response,
    session: Session = Depends(get_session),
) -> UserPublic:
    user = session.exec(select(User).where(User.email == body.email)).first()
    if not user or not user.hashed_password or not verify_password(
        body.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    _set_auth_cookie(response, create_access_token(user.id))  # type: ignore[arg-type]
    return UserPublic.from_user(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout() -> Response:
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(key=settings.AUTH_COOKIE_NAME, path="/")
    return response


@router.get("/me", response_model=UserPublic)
def me(current_user: User = Depends(get_current_user)) -> UserPublic:
    return UserPublic.from_user(current_user)


@router.patch("/me", response_model=UserPublic)
def update_me(
    body: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> UserPublic:
    data = body.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(current_user, key, value)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return UserPublic.from_user(current_user)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    body: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Response:
    if not current_user.hashed_password or not verify_password(
        body.current_password, current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )
    current_user.hashed_password = hash_password(body.new_password)
    current_user.password_changed_at = datetime.utcnow()
    session.add(current_user)
    session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
