import uuid
from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from app.core.database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    game_key = Column(String(50), nullable=False, index=True)

    question_text = Column(Text, nullable=False)

    options = Column(ARRAY(String), nullable=True)

    correct_answer = Column(String(255), nullable=False)

    difficulty = Column(String(20), nullable=True, index=True)

    is_public = Column(Boolean, default=True, nullable=False, index=True)

    owner_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    owner = relationship("User")

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner1 = relationship("User", back_populates="questions")