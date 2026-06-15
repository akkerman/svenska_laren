from sqlalchemy import Column, Integer, String, Float, Date, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(String, primary_key=True)
    difficulty = Column(Float, default=0.3)

class WordCard(Base):
    __tablename__ = "word_cards"

    id = Column(Integer, primary_key=True, index=True)
    swedish = Column(String, index=True)
    dutch = Column(String)
    notes = Column(String, nullable=True)  # Context/notes: e.g. "possessive" or "auxiliary verb"
    frequency_rank = Column(Integer, default=1000)  # Lower = more frequent
    direction = Column(String, default="se_nl")  # "se_nl" or "nl_se"
    box = Column(Integer, default=1)
    next_review = Column(Date)
    total_correct = Column(Integer, default=0)
    total_wrong = Column(Integer, default=0)

class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    role = Column(String)
    content = Column(String)
    created_at = Column(DateTime, server_default=func.now())

class TranslationSession(Base):
    __tablename__ = "translation_sessions"

    id = Column(Integer, primary_key=True, index=True)
    direction = Column(String)
    topic = Column(String)
    source_sentence = Column(String)
    user_attempt = Column(String)
    llm_feedback = Column(String)
    score = Column(Integer)
    difficulty = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
