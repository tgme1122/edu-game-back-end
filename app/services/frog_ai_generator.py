import json
from typing import List, Literal

from google import genai
from pydantic import BaseModel, Field, ValidationError

from app.schemas.frog_game import (
    FrogGameQuestionGenerateRequest,
    FrogGameGeneratedQuestion,
)

client = genai.Client()


class GeneratedQuestionSchema(BaseModel):
    question_text: str = Field(description="Quiz question text")
    options: List[str] = Field(description="Answer options")
    correct_answer: str = Field(description="Correct option text")
    difficulty: Literal["easy", "medium", "hard"]


class GeneratedQuestionsWrapper(BaseModel):
    questions: List[GeneratedQuestionSchema]


def generate_frog_quiz_questions_with_gemini(
    payload: FrogGameQuestionGenerateRequest,
) -> List[FrogGameGeneratedQuestion]:
    option_count = 3 if payload.question_type == "mcq-3" else 5

    prompt = f"""
You are generating educational multiple-choice questions for a frog quiz game.

Requirements:
- Topic: {payload.topic}
- Difficulty: {payload.difficulty}
- Language: {payload.language}
- Number of questions: {payload.limit}
- Subject: {payload.subject or "general"}
- Each question must have exactly {option_count} options
- Only one option must be correct
- Questions must be clear, short, and suitable for learners
- Do not repeat questions
- correct_answer must exactly match one item from options
- Return only JSON matching the schema
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_json_schema": GeneratedQuestionsWrapper.model_json_schema(),
        },
    )

    if not response.text:
        raise ValueError("Gemini bo'sh javob qaytardi")

    try:
        parsed = GeneratedQuestionsWrapper.model_validate_json(response.text)
    except ValidationError as e:
        raise ValueError(f"Gemini javobi schema ga mos emas: {str(e)}")
    except Exception:
        raise ValueError(f"Gemini noto'g'ri JSON qaytardi: {response.text[:300]}")

    cleaned: List[FrogGameGeneratedQuestion] = []

    for item in parsed.questions:
        question_text = item.question_text.strip()
        options = [str(x).strip() for x in item.options if str(x).strip()]
        correct_answer = item.correct_answer.strip()

        unique_options = []
        seen = set()
        for opt in options:
            normalized = opt.strip()
            if normalized not in seen:
                seen.add(normalized)
                unique_options.append(normalized)

        if not question_text:
            continue

        if len(unique_options) != option_count:
            continue

        if correct_answer not in unique_options:
            continue

        cleaned.append(
            FrogGameGeneratedQuestion(
                question_text=question_text,
                options=unique_options,
                correct_answer=correct_answer,
                difficulty=item.difficulty,
                subject=payload.subject,
            )
        )

    if not cleaned:
        raise ValueError("Valid savollar generatsiya bo'lmadi")

    return cleaned[: payload.limit]