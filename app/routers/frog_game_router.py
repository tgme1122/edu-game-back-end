from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from app.core.database import get_db
from app.models.frog_game import FrogGameQuestion
from app.schemas.frog_game import (
    FrogGameQuestionCreate,
    FrogGameQuestionUpdate,
    FrogGameQuestionOut,
    FrogGameQuestionGenerateRequest,
    FrogGameGenerateResponse,
)
from app.dependencies.auth import get_current_user
from app.models.users import User
from app.services.frog_ai_generator import generate_frog_quiz_questions_with_gemini


router = APIRouter(
    prefix="/frog-game-questions",
    tags=["Frog Game Questions"]
)


@router.post("/generate", response_model=FrogGameGenerateResponse)
def generate_questions_with_ai(
    payload: FrogGameQuestionGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        generated_questions = generate_frog_quiz_questions_with_gemini(payload)
        saved_questions = []

        for item in generated_questions:
            question = FrogGameQuestion(
                id=uuid.uuid4(),  # str emas, uuid object
                game_key=payload.game_key,
                question_text=item.question_text,
                options=item.options,
                correct_answer=item.correct_answer,
                difficulty=item.difficulty or payload.difficulty,
                is_public=payload.is_public,
                owner_user_id=current_user.id,
                subject=payload.subject,
            )
            db.add(question)
            saved_questions.append(question)

        db.commit()

        for q in saved_questions:
            db.refresh(q)

        return {
            "message": "AI savollar yaratildi va DB ga saqlandi",
            "count": len(saved_questions),
            "questions": saved_questions,
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[FrogGameQuestionOut])
def get_questions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    questions = db.query(FrogGameQuestion).filter(
        FrogGameQuestion.game_key == "frog-quiz",
        (
            (FrogGameQuestion.is_public == True) |
            (FrogGameQuestion.owner_user_id == current_user.id)
        )
    ).all()

    return questions


@router.get("/{question_id}", response_model=FrogGameQuestionOut)
def get_question(
    question_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    question = db.query(FrogGameQuestion).filter(
        FrogGameQuestion.id == question_id
    ).first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    if not question.is_public and question.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    return question


@router.post("/", response_model=FrogGameQuestionOut)
def create_question(
    data: FrogGameQuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    question = FrogGameQuestion(
        id=uuid.uuid4(),  # str emas
        game_key=data.game_key,
        question_text=data.question_text,
        options=data.options,
        correct_answer=data.correct_answer,
        difficulty=data.difficulty,
        is_public=data.is_public,
        owner_user_id=current_user.id,
        subject=data.subject,
    )

    db.add(question)
    db.commit()
    db.refresh(question)

    return question


@router.put("/{question_id}", response_model=FrogGameQuestionOut)
def update_question(
    question_id: str,
    data: FrogGameQuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    question = db.query(FrogGameQuestion).filter(
        FrogGameQuestion.id == question_id
    ).first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    if question.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You cannot edit this question")

    if data.question_text is not None:
        question.question_text = data.question_text
    if data.options is not None:
        question.options = data.options
    if data.correct_answer is not None:
        question.correct_answer = data.correct_answer
    if data.difficulty is not None:
        question.difficulty = data.difficulty
    if data.is_public is not None:
        question.is_public = data.is_public
    if data.subject is not None:
        question.subject = data.subject

    db.commit()
    db.refresh(question)

    return question


@router.delete("/{question_id}")
def delete_question(
    question_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    question = db.query(FrogGameQuestion).filter(
        FrogGameQuestion.id == question_id
    ).first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    if question.owner_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You cannot delete this question")

    db.delete(question)
    db.commit()

    return {"message": "Question deleted successfully"}