# app/models/frog_game_question.py

from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid

from app.core.database import Base


class FrogGameQuestion(Base):

    __tablename__ = "frog_game_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    game_key = Column(String, nullable=False)

    question_text = Column(String, nullable=False)

    options = Column(ARRAY(String))

    correct_answer = Column(String, nullable=False)

    difficulty = Column(String, nullable=False)

    is_public = Column(Boolean, default=True)

    owner_user_id = Column(UUID(as_uuid=True), nullable=True)

    subject = Column(String, nullable=True)