from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from uuid import UUID


class FrogGameQuestionBase(BaseModel):
    game_key: str
    question_text: str
    options: Optional[List[str]] = None
    correct_answer: str
    difficulty: Optional[str] = None
    is_public: bool = True
    subject: Optional[str] = None


class FrogGameQuestionCreate(FrogGameQuestionBase):
    pass


class FrogGameQuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    difficulty: Optional[str] = None
    is_public: Optional[bool] = None
    subject: Optional[str] = None


class FrogGameQuestionOut(FrogGameQuestionBase):
    id: UUID
    owner_user_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class FrogGameQuestionGenerateRequest(BaseModel):
    limit: int = Field(..., ge=1, le=20)
    topic: str = Field(..., min_length=2, max_length=300)
    question_type: Literal["mcq-3", "mcq-5"]
    difficulty: Literal["easy", "medium", "hard"]
    language: Literal["uz", "en"] = "uz"
    game_key: str = "frog-quiz"
    is_public: bool = True
    subject: Optional[str] = None


class FrogGameGeneratedQuestion(BaseModel):
    question_text: str
    options: List[str]
    correct_answer: str
    difficulty: Optional[str] = None
    subject: Optional[str] = None


class FrogGameGenerateResponse(BaseModel):
    message: str
    count: int
    questions: List[FrogGameQuestionOut]