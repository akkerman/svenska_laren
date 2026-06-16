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
    lang_from_name = "DUTCH" if request.direction == "nl_to_se" else "SWEDISH"
    lang_to_name = "SWEDISH" if request.direction == "nl_to_se" else "DUTCH"

    difficulty_instr = get_difficulty_instruction(request.difficulty)
    topic_str = f"Topic: {request.topic}." if request.topic else ""

    # Get weighted wordlist for context
    direction = "se_nl" if request.direction == "se_to_nl" else "nl_se"
    wordlist = get_weighted_wordlist(direction, db)
    wordlist_str = json.dumps(wordlist[:100])  # Limit to 100 words for token efficiency

    prompt = f"""Generate ONE sentence pair in JSON format.

TASK: Create ONE sentence in {lang_from_name} and translate it to {lang_to_name}.
{difficulty_instr}
{topic_str}

CRITICAL:
- "sentence" field MUST contain the {lang_from_name} sentence
- "translation" field MUST contain the {lang_to_name} translation
- Return ONLY valid JSON, no explanation:
{{"sentence": "one sentence in {lang_from_name}", "translation": "its translation in {lang_to_name}"}}"""

    system = f"""You are a Swedish language teacher. You MUST:
1. Generate ONE sentence in {lang_from_name}
2. Translate it to {lang_to_name}
3. Return ONLY valid JSON with TWO fields: "sentence" and "translation"
4. Prefer these words when possible: {wordlist_str}
5. Do NOT return lists, word lists, or multiple items
6. Do NOT include any text outside the JSON"""
    response_text = ollama.generate(prompt, system)

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

        # Validate: sentence should be in correct language
        # For SE→NL: sentence should contain Swedish (not Dutch articles like "de", "het")
        # For NL→SE: sentence should contain Dutch (not Swedish articles)
        if request.direction == "se_to_nl":
            dutch_words = {"de", "het", "een", "is", "ben", "zijn"}
            sentence_words = set(sentence.lower().split())
            if len(sentence_words & dutch_words) > len(sentence_words) * 0.3:  # >30% Dutch words
                # Likely Dutch sentence, swap them
                sentence, translation = translation, sentence
        elif request.direction == "nl_to_se":
            swedish_words = {"den", "det", "en", "är", "på", "och"}
            sentence_words = set(sentence.lower().split())
            if len(sentence_words & swedish_words) > len(sentence_words) * 0.3:  # >30% Swedish words
                # Likely Swedish sentence, swap them
                sentence, translation = translation, sentence

    except (json.JSONDecodeError, AttributeError, TypeError, ValueError):
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
        correct_translation = data.get("translation", "") if isinstance(data, dict) else ""
    except (json.JSONDecodeError, AttributeError, TypeError, ValueError):
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
