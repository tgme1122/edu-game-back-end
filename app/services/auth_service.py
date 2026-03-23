from fastapi import HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.security import hash_password, verify_password
from app.models.users import User  # User qayerda bo'lsa shu importni moslang


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_name(db: Session, name: str) -> User | None:
    return db.query(User).filter(User.name == name).first()


def get_user_by_id(db: Session, user_id: UUID) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, name: str, email: str, password: str, roles: list[str] | None = None) -> User:
    if get_user_by_email(db, email):
        raise HTTPException(status_code=400, detail="Email already registered")

    if get_user_by_name(db, name):
        raise HTTPException(status_code=400, detail="Name already taken")

    user = User(
        name=name,
        email=email,
        hashed_password=hash_password(password),
        roles=roles or ["user"],
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


def save_refresh_token_hash(db: Session, user: User, refresh_token: str) -> User:
    """
    refresh_token ni o'zini emas, HASH ini saqlaymiz.
    """
    user.refresh_token_hash = hash_password(refresh_token)
    db.commit()
    db.refresh(user)
    return user


def clear_refresh_token_hash(db: Session, user: User) -> User:
    user.refresh_token_hash = None
    db.commit()
    db.refresh(user)
    return user


def verify_refresh_token(db: Session, user: User, refresh_token: str) -> bool:
    """
    DB'dagi refresh_token_hash bilan kelgan refresh_token mosligini tekshiradi.
    """
    if not user.refresh_token_hash:
        return False
    return verify_password(refresh_token, user.refresh_token_hash)