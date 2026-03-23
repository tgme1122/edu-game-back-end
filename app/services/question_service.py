from typing import Optional, List
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.questions import Question


class QuestionService:
    @staticmethod
    def get_public_questions(db: Session, game_key: str, limit: int = 50) -> List[Question]:
        return (
            db.query(Question)
            .filter(Question.game_key == game_key, Question.is_public == True)
            .order_by(Question.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_my_questions(db: Session, user_id: UUID, game_key: str, limit: int = 200) -> List[Question]:
        return (
            db.query(Question)
            .filter(
                Question.game_key == game_key,
                Question.is_public == False,
                Question.owner_user_id == user_id,
            )
            .order_by(Question.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def create_my_question(
        db: Session,
        user_id: UUID,
        *,
        game_key: str,
        question_text: str,
        options: Optional[list[str]],
        correct_answer: str,
        difficulty: Optional[str] = None,
    ) -> Question:
        q = Question(
            game_key=game_key,
            question_text=question_text,
            options=options,
            correct_answer=correct_answer,
            difficulty=difficulty,
            is_public=False,
            owner_user_id=user_id,
        )
        db.add(q)
        db.commit()
        db.refresh(q)
        return q

    @staticmethod
    def delete_my_question(db: Session, user_id: UUID, question_id: UUID) -> None:
        q = (
            db.query(Question)
            .filter(
                Question.id == question_id,
                Question.owner_user_id == user_id,
                Question.is_public == False,
            )
            .first()
        )
        if not q:
            return  # yoki Exception ko'tarasiz
        db.delete(q)
        db.commit()

    @staticmethod
    def update_my_question(
        db: Session,
        user_id: UUID,
        question_id: UUID,
        *,
        question_text: Optional[str] = None,
        options: Optional[list[str]] = None,
        correct_answer: Optional[str] = None,
        difficulty: Optional[str] = None,
    ) -> Optional[Question]:
        q = (
            db.query(Question)
            .filter(
                Question.id == question_id,
                Question.owner_user_id == user_id,
                Question.is_public == False,
            )
            .first()
        )
        if not q:
            return None

        if question_text is not None:
            q.question_text = question_text
        if options is not None:
            q.options = options
        if correct_answer is not None:
            q.correct_answer = correct_answer
        if difficulty is not None:
            q.difficulty = difficulty

        db.commit()
        db.refresh(q)
        return q