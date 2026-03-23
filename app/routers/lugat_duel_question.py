from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.users import User
from app.services.lugat_duel_question import (
    create_lugat_duel_question,
    bulk_create_lugat_duel_questions,
    get_lugat_duel_questions,
    get_lugat_duel_question_by_id,
    update_lugat_duel_question,
    delete_lugat_duel_question,
)
from app.schemas.lugat_duel_question import (
    LugatDuelQuestionCreate,
    LugatDuelQuestionUpdate,
    LugatDuelQuestionOut,
    LugatDuelQuestionGenerateRequest,
    LugatDuelQuestionGenerateResponse,
)
from app.services.lugat_duel_ai_service import generate_lugat_duel_questions_with_gemini

router = APIRouter(
    prefix="/lugat-duel",
    tags=["Lugat Duel"],
)


@router.post(
    "/questions",
    response_model=LugatDuelQuestionOut,
    status_code=status.HTTP_201_CREATED,
)
def create_question(
    payload: LugatDuelQuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_lugat_duel_question(
        db=db,
        payload=payload,
        owner_user_id=current_user.id,
    )


@router.get("/questions", response_model=list[LugatDuelQuestionOut])
def list_questions(
    subject: Optional[str] = Query(default=None),
    only_public: bool = Query(default=False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_lugat_duel_questions(
        db=db,
        owner_user_id=current_user.id,
        subject=subject,
        only_public=only_public,
    )


@router.get("/questions/{question_id}", response_model=LugatDuelQuestionOut)
def get_question(
    question_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obj = get_lugat_duel_question_by_id(db=db, question_id=question_id)

    if not obj:
        raise HTTPException(status_code=404, detail="Savol topilmadi")

    if not obj.is_public and obj.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Ruxsat yo'q")

    return obj


@router.put("/questions/{question_id}", response_model=LugatDuelQuestionOut)
def update_question(
    question_id: UUID,
    payload: LugatDuelQuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obj = get_lugat_duel_question_by_id(db=db, question_id=question_id)

    if not obj:
        raise HTTPException(status_code=404, detail="Savol topilmadi")

    if obj.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Siz bu savolni o'zgartira olmaysiz")

    return update_lugat_duel_question(db=db, obj=obj, payload=payload)


@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_question(
    question_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    obj = get_lugat_duel_question_by_id(db=db, question_id=question_id)

    if not obj:
        raise HTTPException(status_code=404, detail="Savol topilmadi")

    if obj.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Siz bu savolni o'chira olmaysiz")

    delete_lugat_duel_question(db=db, obj=obj)
    return None


@router.post(
    "/questions/ai-generate",
    response_model=LugatDuelQuestionGenerateResponse,
    status_code=status.HTTP_201_CREATED,
)
def ai_generate_questions(
    payload: LugatDuelQuestionGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        generated = generate_lugat_duel_questions_with_gemini(payload)

        create_items = [
            LugatDuelQuestionCreate(
                game_key="lugat-duel",
                question_text=item.question_text,
                options=item.options,
                correct_answer=item.correct_answer,
                is_public=payload.is_public,
                subject=item.subject or payload.subject,
            )
            for item in generated
        ]

        created = bulk_create_lugat_duel_questions(
            db=db,
            items=create_items,
            owner_user_id=current_user.id,
        )

        return LugatDuelQuestionGenerateResponse(items=created)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))