from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import TranslationSession
from schemas import (
    TranslationGenerateRequest, TranslationGenerateResponse,
    TranslationEvaluateRequest, TranslationEvaluateResponse
)
from .vocabulary import get_weighted_wordlist
import ollama
import json

router = APIRouter(prefix="/api/translation", tags=["translation"])

DIFFICULTY_INSTRUCTIONS = {
    "low": "Use very simple vocabulary, present tense, short sentences (5–8 words).",
    "medium": "Use everyday vocabulary, mix of tenses, moderate length (8–12 words).",
    "high": "Use varied vocabulary including idioms, compound sentences (12–18 words).",
    "advanced": "Use advanced vocabulary, subjunctive, complex grammar, longer sentences."
}

def get_difficulty_instruction(difficulty: float) -> str:
    if difficulty < 0.3:
        return DIFFICULTY_INSTRUCTIONS["low"]
    elif difficulty < 0.6:
        return DIFFICULTY_INSTRUCTIONS["medium"]
    elif difficulty < 0.85:
        return DIFFICULTY_INSTRUCTIONS["high"]
    else:
        return DIFFICULTY_INSTRUCTIONS["advanced"]

@router.post("/generate", response_model=TranslationGenerateResponse)
def generate_translation(request: TranslationGenerateRequest, db: Session = Depends(get_db)):
    lang_from = "Dutch" if request.direction == "nl_to_se" else "Swedish"
    lang_to = "Swedish" if request.direction == "nl_to_se" else "Dutch"

    difficulty_instr = get_difficulty_instruction(request.difficulty)
    topic_str = f"Topic: {request.topic}." if request.topic else ""

    # Get weighted wordlist for context
    direction = "se_nl" if request.direction == "se_to_nl" else "nl_se"
    wordlist = get_weighted_wordlist(direction, db)
    wordlist_str = json.dumps(wordlist[:100])  # Limit to 100 words for token efficiency

    prompt = f"""Generate a sentence pair in JSON format.

Generate a single natural sentence in {lang_from} and provide the correct translation to {lang_to}. {difficulty_instr}. {topic_str}

PREFERRED VOCABULARY (prioritize marked words): {wordlist_str}

Return ONLY valid JSON (no markdown, no backticks):
{{"sentence": "the {lang_from} sentence", "translation": "the {lang_to} translation"}}"""

    system = "You are a helpful language teaching assistant. Preferably use words from the provided vocabulary list, especially those marked as 'priority': true. Return ONLY valid JSON."
    response_text = ollama.generate(prompt, system)

    try:
        data = json.loads(response_text)
        sentence = data.get("sentence", "")
        translation = data.get("translation", "")
    except json.JSONDecodeError:
        # Fallback if JSON parsing fails
        sentence = response_text
        translation = ""

    return {
        "sentence": sentence,
        "language_from": lang_from,
        "language_to": lang_to
    }

@router.post("/evaluate", response_model=TranslationEvaluateResponse)
def evaluate_translation(request: TranslationEvaluateRequest, db: Session = Depends(get_db)):
    lang_src = "Swedish" if request.direction == "se_to_nl" else "Dutch"
    lang_tgt = "Dutch" if request.direction == "se_to_nl" else "Swedish"

    prompt = f"""Provide the correct translation only.

ORIGINEEL ({lang_src}): {request.source_sentence}

Translate this to {lang_tgt}. Return ONLY valid JSON (no markdown):
{{"translation": "the correct translation in {lang_tgt}"}}"""

    system = f"You are a translator. Return ONLY valid JSON with the correct translation in {lang_tgt}."

    try:
        response_text = ollama.generate(prompt, system)
        data = json.loads(response_text)
        correct_translation = data.get("translation", "")
    except json.JSONDecodeError:
        correct_translation = ""

    session = TranslationSession(
        direction=request.direction,
        source_sentence=request.source_sentence,
        user_attempt=request.user_attempt,
        llm_feedback="",
        score=0,
        difficulty=request.difficulty
    )
    db.add(session)
    db.commit()

    return {
        "source_sentence": request.source_sentence,
        "user_attempt": request.user_attempt,
        "correct_translation": correct_translation
    }
