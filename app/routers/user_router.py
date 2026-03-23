from __future__ import annotations

import os
import uuid
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password
from app.dependencies.auth import get_current_user
from app.dependencies.roles import require_admin
from app.models.users import User
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["Users"])

AVATAR_DIR = "app/static/uploads/avatars"
ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2MB


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UserOut)
def update_me(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = user_data.model_dump(exclude_unset=True)
    data.pop("roles", None)  # rolesni faqat admin o'zgartiradi

    # unique checks
    if "email" in data and data["email"] != current_user.email:
        if user_service.check_email(db, data["email"]):
            raise HTTPException(status_code=400, detail="Email already registered")

    if "name" in data and data["name"] != current_user.name:
        if user_service.check_name(db, data["name"]):
            raise HTTPException(status_code=400, detail="Name already taken")

    # password update
    if "password" in data and data["password"]:
        current_user.hashed_password = hash_password(data["password"])
        data.pop("password", None)

    # set other fields
    for k, v in data.items():
        setattr(current_user, k, v)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/me/avatar", response_model=UserOut)
async def upload_my_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files allowed")

    os.makedirs(AVATAR_DIR, exist_ok=True)

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTS:
        raise HTTPException(status_code=400, detail="Allowed: jpg, jpeg, png, webp")

    content = await file.read()
    if len(content) > MAX_AVATAR_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 2MB)")

    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(AVATAR_DIR, filename)

    with open(path, "wb") as f:
        f.write(content)

    old = current_user.avatar

    current_user.avatar = f"/static/uploads/avatars/{filename}"
    db.commit()
    db.refresh(current_user)
    try:
        if old and old.startswith("/static/uploads/avatars/"):
            old_filename = old.split("/static/uploads/avatars/")[-1]
            old_path = os.path.join(AVATAR_DIR, old_filename)
            if os.path.exists(old_path) and os.path.isfile(old_path):
                os.remove(old_path)
    except Exception:
        # log qilmoqchi bo'lsangiz shu yerga logger qo'ying
        pass

    return current_user


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, user)


@router.get("/", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return user_service.get_users(db)


@router.get("/{user_id}", response_model=UserOut)
def get_user_by_id(
    user_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    db_user = user_service.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return user_service.update_user(db, user_id, user_data)


@router.patch("/{user_id}/roles", response_model=UserOut)
def update_roles(
    user_id: UUID,
    roles: list[str],
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return user_service.update_user_roles(db, user_id, roles)


@router.delete("/{user_id}", status_code=204)
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    user_service.delete_user(db, user_id)
    return None