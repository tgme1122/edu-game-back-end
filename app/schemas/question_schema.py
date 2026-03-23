from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class QuestionCreate(BaseModel):
    game_key: str
    question_text: str
    options: Optional[List[str]] = None
    correct_answer: str
    difficulty: Optional[str] = None
    is_public: bool = False

class QuestionOut(BaseModel):
    id: UUID
    game_key: str
    question_text: str
    options: Optional[List[str]] = None
    correct_answer: str
    difficulty: Optional[str] = None
    is_public: bool
    owner_user_id: Optional[UUID] = None

    class Config:
        from_attributes = True