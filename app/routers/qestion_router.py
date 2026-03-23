from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.schemas.question_schema import QuestionCreate, QuestionOut
from app.services.question_service import QuestionService

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.get("", response_model=list[QuestionOut])
def public_questions(
    game_key: str = Query(...),
    db: Session = Depends(get_db),
):
    return QuestionService.get_public_questions(db, game_key=game_key)


@router.get("/my", response_model=list[QuestionOut])
def my_questions(
    game_key: str = Query(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return QuestionService.get_my_questions(db, user_id=current_user.id, game_key=game_key)


@router.post("/my", response_model=QuestionOut)
def add_my_question(
    payload: QuestionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
 

    return QuestionService.create_my_question(
        db,
        current_user.id,
        game_key=payload.game_key,
        question_text=payload.question_text,
        options=payload.options,
        correct_answer=payload.correct_answer,
        difficulty=payload.difficulty,
    )