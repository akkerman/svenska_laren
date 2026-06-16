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
    # Determine direction
    is_nl_to_se = request.direction == "nl_to_se"
    lang_from = "Dutch" if is_nl_to_se else "Swedish"
    lang_to = "Swedish" if is_nl_to_se else "Dutch"

    difficulty_instr = get_difficulty_instruction(request.difficulty)
    topic_str = f"Topic: {request.topic}." if request.topic else ""

    # Get weighted wordlist for context
    direction = "nl_se" if is_nl_to_se else "se_nl"
    wordlist = get_weighted_wordlist(direction, db)
    wordlist_str = json.dumps(wordlist[:50])  # Limit to 50 words

    if is_nl_to_se:
        prompt = f"""{difficulty_instr} {topic_str}

Generate ONE sentence pair. The sentence must be in DUTCH.

EXAMPLE OUTPUT (this is the ONLY acceptable format):
{{"sentence": "Ik hou van katten", "translation": "Jag älskar katter"}}

Your response MUST be EXACTLY like the example above.
SENTENCE IN DUTCH ONLY.
TRANSLATION IN SWEDISH ONLY.
NO OTHER TEXT ALLOWED."""
        system = """You are a Dutch-to-Swedish translator for language teaching.
Your ONLY job is to return valid JSON.
The "sentence" field MUST be in DUTCH.
The "translation" field MUST be in SWEDISH.
Return ONLY the JSON object, nothing else. No explanation, no markdown, no extra text."""
    else:
        prompt = f"""{difficulty_instr} {topic_str}

Generate ONE sentence pair. The sentence must be in SWEDISH.

EXAMPLE OUTPUT (this is the ONLY acceptable format):
{{"sentence": "Jag älskar katter", "translation": "Ik hou van katten"}}

Your response MUST be EXACTLY like the example above.
SENTENCE IN SWEDISH ONLY.
TRANSLATION IN DUTCH ONLY.
NO OTHER TEXT ALLOWED."""
        system = """You are a Swedish-to-Dutch translator for language teaching.
Your ONLY job is to return valid JSON.
The "sentence" field MUST be in SWEDISH.
The "translation" field MUST be in DUTCH.
Return ONLY the JSON object, nothing else. No explanation, no markdown, no extra text."""

    response_text = ollama.generate(prompt, system)
    print(f"[TRANSLATION] Direction: {request.direction}")
    print(f"[TRANSLATION] AI Response: {response_text}")

    try:
        # Extract JSON from response (may contain markdown or explanation)
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
        else:
            json_str = response_text

        data = json.loads(json_str)
        # Handle case where AI returns a list instead of dict
        if isinstance(data, list) and len(data) > 0:
            data = data[0]
        sentence = data.get("sentence", "") if isinstance(data, dict) else ""
        translation = data.get("translation", "") if isinstance(data, dict) else ""

    except (json.JSONDecodeError, AttributeError, TypeError, ValueError):
        # If parsing fails, log it and return empty
        print(f"[TRANSLATION ERROR] Failed to parse response: {response_text}")
        sentence = ""
        translation = ""

    return {
        "sentence": sentence,
        "language_from": lang_from,
        "language_to": lang_to,
        "correct_translation": translation
    }

@router.post("/evaluate", response_model=TranslationEvaluateResponse)
def evaluate_translation(request: TranslationEvaluateRequest, db: Session = Depends(get_db)):
    # The correct translation is passed from frontend (from /generate response)
    # We don't need to ask AI again
    correct_translation = getattr(request, 'correct_translation', '')

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
