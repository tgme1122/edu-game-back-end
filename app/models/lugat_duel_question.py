import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from app.core.database import Base


class LugatDuelQuestion(Base):
    __tablename__ = "lugat_duel_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    game_key = Column(String, nullable=False, index=True, default="lugat-duel")
    question_text = Column(String, nullable=False)
    options = Column(ARRAY(String), nullable=True)
    correct_answer = Column(String, nullable=False)
    is_public = Column(Boolean, default=True)
    owner_user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    subject = Column(String, nullable=True, index=True)