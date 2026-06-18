from pydantic import BaseModel
from typing import Optional
from datetime import date

class SettingsResponse(BaseModel):
    difficulty: float

class SettingsUpdate(BaseModel):
    difficulty: float

class WordCardResponse(BaseModel):
    id: int
    swedish: str
    dutch: str
    notes: Optional[str] = None
    frequency_rank: int
    box: int
    next_review: Optional[date]
    total_correct: int
    total_wrong: int
    direction: str

    class Config:
        from_attributes = True

class WordCardCreate(BaseModel):
    swedish: str
    dutch: str

class CardAnswerRequest(BaseModel):
    card_id: int
    correct: bool

class CardAnswerResponse(BaseModel):
    new_box: int
    next_review: Optional[date]

class BoxCount(BaseModel):
    filtered: int
    total: int

class CardStatsResponse(BaseModel):
    total: int
    mastered: int
    per_box: list[BoxCount]

class TranslationGenerateRequest(BaseModel):
    direction: str
    topic: Optional[str] = None
    difficulty: float
    exclude_sentence: Optional[str] = None

class TranslationGenerateResponse(BaseModel):
    sentence: str
    language_from: str
    language_to: str
    correct_translation: str

class TranslationEvaluateRequest(BaseModel):
    source_sentence: str
    user_attempt: str
    direction: str
    difficulty: float
    correct_translation: str

class TranslationEvaluateResponse(BaseModel):
    source_sentence: str
    user_attempt: str
    correct_translation: str

class ConversationStartRequest(BaseModel):
    topic: str
    difficulty: float

class ConversationStartResponse(BaseModel):
    session_id: str
    opening_message: str

class ConversationMessageRequest(BaseModel):
    session_id: str
    user_message: str
    difficulty: float

class MessageResponse(BaseModel):
    role: str
    content: str

    class Config:
        from_attributes = True
