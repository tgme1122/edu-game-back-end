from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from uuid import UUID

from app.core.database import get_db
from app.core.config import settings
from app.core.jwt import create_token, decode_token
from app.core.security import hash_password, verify_password

from app.dependencies.auth import get_current_user
from app.models.users import User  # sizda User shu faylda bo'lsa

from app.schemas.auth_schema import (
    RegisterSchema,
    LoginSchema,
    RefreshSchema,
    LoginResponse,
    TokenResponse,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


def _save_refresh_hash(db: Session, user: User, refresh_hash: str):
    user.refresh_token_hash = refresh_hash
    db.commit()
    db.refresh(user)


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterSchema, db: Session = Depends(get_db)):
    # email unique
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # name unique
    if db.query(User).filter(User.name == data.name).first():
        raise HTTPException(status_code=400, detail="Name already taken")

    user = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
        roles=["user"],  # default
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_token(
        payload={"sub": str(user.id), "type": "access", "roles": user.roles},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_token(
        payload={"sub": str(user.id), "type": "refresh"},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    _save_refresh_hash(db, user, hash_password(refresh_token))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user,
    }


@router.post("/login", response_model=LoginResponse)
def login(data: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    access_token = create_token(
        payload={"sub": str(user.id), "type": "access", "roles": user.roles},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_token(
        payload={"sub": str(user.id), "type": "refresh"},
        expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    _save_refresh_hash(db, user, hash_password(refresh_token))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user,
    }


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: RefreshSchema, db: Session = Depends(get_db)):
    payload = decode_token(data.refresh_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Not a refresh token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # user_id uuid bo'lishi kerak
    try:
        user_uuid = UUID(user_id)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid user id in token")

    user = db.query(User).filter(User.id == user_uuid).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    # refresh token hash tekshiruv
    if not user.refresh_token_hash or not verify_password(data.refresh_token, user.refresh_token_hash):
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    access_token = create_token(
        payload={"sub": str(user.id), "type": "access", "roles": user.roles},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return {"access_token": access_token, "refresh_token": data.refresh_token, "token_type": "bearer"}


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _save_refresh_hash(db, current_user, "")
    return {"msg": "Successfully logged out"}