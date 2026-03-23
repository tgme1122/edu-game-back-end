from typing import List, Literal

from google import genai
from pydantic import BaseModel, Field, ValidationError

from app.schemas.lugat_duel_question import (
    LugatDuelQuestionGenerateRequest,
    LugatDuelGeneratedQuestion,
)

client = genai.Client()


class GeneratedQuestionSchema(BaseModel):
    question_text: str = Field(description="Quiz question text")
    options: List[str] = Field(description="Answer options")
    correct_answer: str = Field(description="Correct option text")
    difficulty: Literal["easy", "medium", "hard"]


class GeneratedQuestionsWrapper(BaseModel):
    questions: List[GeneratedQuestionSchema]


def generate_lugat_duel_questions_with_gemini(
    payload: LugatDuelQuestionGenerateRequest,
) -> List[LugatDuelGeneratedQuestion]:
    option_count = 4

    prompt = f"""
You are generating educational vocabulary duel multiple-choice questions.

Requirements:
- Topic: {payload.topic}
- Difficulty: {payload.difficulty}
- Language: {payload.language}
- Number of questions: {payload.limit}
- Subject: {payload.subject or "general"}
- Each question must have exactly {option_count} options
- Only one option must be correct
- Questions must be clear, short, and suitable for learners
- Prefer translation, synonym, antonym, word meaning, spelling, and simple usage questions
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

    cleaned: List[LugatDuelGeneratedQuestion] = []
    seen_questions = set()

    for item in parsed.questions:
        question_text = item.question_text.strip()
        correct_answer = item.correct_answer.strip()

        if not question_text or not correct_answer:
            continue

        unique_options = []
        seen_opts = set()

        for opt in item.options:
            text = str(opt).strip()
            normalized = text.lower()
            if text and normalized not in seen_opts:
                seen_opts.add(normalized)
                unique_options.append(text)

        normalized_question = question_text.lower()
        if normalized_question in seen_questions:
            continue

        if len(unique_options) != option_count:
            continue

        normalized_options = [opt.lower() for opt in unique_options]
        normalized_correct = correct_answer.lower()

        if normalized_correct not in normalized_options:
            continue

        real_correct_answer = unique_options[normalized_options.index(normalized_correct)]

        seen_questions.add(normalized_question)

        cleaned.append(
            LugatDuelGeneratedQuestion(
                question_text=question_text,
                options=unique_options,
                correct_answer=real_correct_answer,
                difficulty=item.difficulty,
                subject=payload.subject,
            )
        )

    if not cleaned:
        raise ValueError("Valid savollar generatsiya bo'lmadi")

    return cleaned[:payload.limit]