from typing import List, Optional, Literal
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, ConfigDict


class LugatDuelQuestionBase(BaseModel):
    game_key: str = "lugat-duel"
    question_text: str
    options: Optional[List[str]] = None
    correct_answer: str
    is_public: bool = True
    subject: Optional[str] = None

    @field_validator("question_text", "correct_answer")
    @classmethod
    def validate_text_fields(cls, v: str):
        value = str(v).strip()
        if not value:
            raise ValueError("Bo'sh qiymat bo'lishi mumkin emas")
        return value

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, v: Optional[str]):
        if v is None:
            return None
        value = str(v).strip()
        return value or None

    @field_validator("options")
    @classmethod
    def validate_options(cls, v: Optional[List[str]]):
        if v is None:
            return v

        cleaned = []
        seen = set()

        for item in v:
            text = str(item).strip()
            if text and text not in seen:
                seen.add(text)
                cleaned.append(text)

        if len(cleaned) < 2:
            raise ValueError("options kamida 2 ta bo'lishi kerak")

        return cleaned


class LugatDuelQuestionCreate(LugatDuelQuestionBase):
    pass


class LugatDuelQuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    is_public: Optional[bool] = None
    subject: Optional[str] = None

    @field_validator("question_text", "correct_answer")
    @classmethod
    def validate_optional_text_fields(cls, v: Optional[str]):
        if v is None:
            return v
        value = str(v).strip()
        if not value:
            raise ValueError("Bo'sh qiymat bo'lishi mumkin emas")
        return value

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, v: Optional[str]):
        if v is None:
            return None
        value = str(v).strip()
        return value or None

    @field_validator("options")
    @classmethod
    def validate_options(cls, v: Optional[List[str]]):
        if v is None:
            return v

        cleaned = []
        seen = set()

        for item in v:
            text = str(item).strip()
            if text and text not in seen:
                seen.add(text)
                cleaned.append(text)

        if len(cleaned) < 2:
            raise ValueError("options kamida 2 ta bo'lishi kerak")

        return cleaned


class LugatDuelQuestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    game_key: str
    question_text: str
    options: Optional[List[str]] = None
    correct_answer: str
    is_public: bool
    owner_user_id: Optional[UUID] = None
    subject: Optional[str] = None


class LugatDuelGeneratedQuestion(BaseModel):
    question_text: str
    options: List[str]
    correct_answer: str
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    subject: Optional[str] = None


class LugatDuelQuestionGenerateRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=200)
    language: Literal["uz", "en"] = "uz"
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    limit: int = Field(default=5, ge=1, le=20)
    subject: Optional[str] = None
    is_public: bool = True

    @field_validator("topic")
    @classmethod
    def validate_topic(cls, v: str):
        value = str(v).strip()
        if not value:
            raise ValueError("topic bo'sh bo'lishi mumkin emas")
        return value

    @field_validator("subject")
    @classmethod
    def validate_subject(cls, v: Optional[str]):
        if v is None:
            return None
        value = str(v).strip()
        return value or None


class LugatDuelQuestionGenerateResponse(BaseModel):
    items: List[LugatDuelQuestionOut]