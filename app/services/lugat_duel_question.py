from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.lugat_duel_question import LugatDuelQuestion
from app.schemas.lugat_duel_question import (
    LugatDuelQuestionCreate,
    LugatDuelQuestionUpdate,
)

GAME_KEY = "lugat-duel"


def create_lugat_duel_question(
    db: Session,
    payload: LugatDuelQuestionCreate,
    owner_user_id: Optional[UUID] = None,
) -> LugatDuelQuestion:
    obj = LugatDuelQuestion(
        game_key=GAME_KEY,
        question_text=payload.question_text,
        options=payload.options,
        correct_answer=payload.correct_answer,
        is_public=payload.is_public,
        owner_user_id=owner_user_id,
        subject=payload.subject,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def bulk_create_lugat_duel_questions(
    db: Session,
    items: List[LugatDuelQuestionCreate],
    owner_user_id: Optional[UUID] = None,
) -> List[LugatDuelQuestion]:
    objects: List[LugatDuelQuestion] = []

    for payload in items:
        obj = LugatDuelQuestion(
            game_key=GAME_KEY,
            question_text=payload.question_text,
            options=payload.options,
            correct_answer=payload.correct_answer,
            is_public=payload.is_public,
            owner_user_id=owner_user_id,
            subject=payload.subject,
        )
        objects.append(obj)

    db.add_all(objects)
    db.commit()

    for obj in objects:
        db.refresh(obj)

    return objects


def get_lugat_duel_questions(
    db: Session,
    owner_user_id: Optional[UUID] = None,
    subject: Optional[str] = None,
    only_public: bool = False,
) -> List[LugatDuelQuestion]:
    query = db.query(LugatDuelQuestion).filter(
        LugatDuelQuestion.game_key == GAME_KEY
    )

    if only_public:
        query = query.filter(LugatDuelQuestion.is_public.is_(True))
    else:
        query = query.filter(
            or_(
                LugatDuelQuestion.is_public.is_(True),
                LugatDuelQuestion.owner_user_id == owner_user_id,
            )
        )

    if subject:
        query = query.filter(LugatDuelQuestion.subject == subject.strip())

    return query.order_by(LugatDuelQuestion.question_text.asc()).all()


def get_lugat_duel_question_by_id(
    db: Session,
    question_id: UUID,
) -> Optional[LugatDuelQuestion]:
    return (
        db.query(LugatDuelQuestion)
        .filter(
            LugatDuelQuestion.id == question_id,
            LugatDuelQuestion.game_key == GAME_KEY,
        )
        .first()
    )


def update_lugat_duel_question(
    db: Session,
    obj: LugatDuelQuestion,
    payload: LugatDuelQuestionUpdate,
) -> LugatDuelQuestion:
    data = payload.model_dump(exclude_unset=True)

    for key, value in data.items():
        setattr(obj, key, value)

    db.commit()
    db.refresh(obj)
    return obj


def delete_lugat_duel_question(
    db: Session,
    obj: LugatDuelQuestion,
) -> None:
    db.delete(obj)
    db.commit()