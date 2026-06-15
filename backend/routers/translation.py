from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import TranslationSession
from schemas import (
    TranslationGenerateRequest, TranslationGenerateResponse,
    TranslationEvaluateRequest, TranslationEvaluateResponse
)
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

    prompt = f"""You are a Swedish language teaching assistant. Generate a single natural sentence in {lang_from} for a student to translate into {lang_to}. {difficulty_instr}. {topic_str} Return ONLY the sentence, no quotes, no explanation."""

    system = "You are a helpful language teaching assistant."
    sentence = ollama.generate(prompt, system)

    return {
        "sentence": sentence,
        "language_from": lang_from,
        "language_to": lang_to
    }

@router.post("/evaluate", response_model=TranslationEvaluateResponse)
def evaluate_translation(request: TranslationEvaluateRequest, db: Session = Depends(get_db)):
    lang_src = "Swedish" if request.direction == "se_to_nl" else "Dutch"
    lang_tgt = "Dutch" if request.direction == "se_to_nl" else "Swedish"

    difficulty_instr = get_difficulty_instruction(request.difficulty)

    prompt = f"""Je bent een Nederlands taalleraar. Beoordeel deze Zweeds-naar-Nederlands vertaling.

ZEGGEN IN HET {lang_src.upper()} (de taal om te vertalen):
{request.source_sentence}

STUDENT VERTALING IN HET {lang_tgt.upper()} (Nederlandse vertaling):
{request.user_attempt}

TAAK:
1. Lees beide zinnen zorgvuldig
2. Vergelijk ze woord voor woord
3. Bepaal welke woorden/onderdelen fout vertaald zijn
4. Geef concrete feedback in het Nederlands
5. Geef een perfecte vertaling (ALLEEN in het {lang_tgt})

ANTWOORD IN DEZE JSON (meer niets):
{{
  "score": <1-5>,
  "feedback": "<Wat is goed/fout? Wees specifiek welke woorden fout zijn>",
  "corrected": "<Perfecte vertaling, VOLLEDIG in het {lang_tgt}, GEEN {lang_src}>"
}}

KRITIEK: Controleer je antwoord:
- Is feedback in het Nederlands?
- Noem je SPECIFIEKE woorden die fout zijn?
- Bevat corrected GEEN {lang_src} woorden?
- Is corrected geldige JSON?"""

    system = f"""Je bent een taalleraar. Antwoord ALLEEN in geldige JSON, niets anders.

DRIE DINGEN:
1. Feedback in het Nederlands - wat is goed/fout in de studentvertaling
2. Score 1-5 - hoe goed is de vertaling
3. Corrected - de perfecte vertaling in het {lang_tgt}

KRITIEK VOOR JOU:
- Controleer dat je output geldige JSON is
- 'corrected' mag GEEN {lang_src} woorden bevatten
- Geef specifieke feedback, niet vaag"""

    try:
        response_text = ollama.generate(prompt, system)
        result = json.loads(response_text)
    except json.JSONDecodeError:
        result = {
            "score": 3,
            "feedback": "Unable to evaluate at the moment.",
            "corrected": request.user_attempt
        }

    session = TranslationSession(
        direction=request.direction,
        source_sentence=request.source_sentence,
        user_attempt=request.user_attempt,
        llm_feedback=result.get("feedback", ""),
        score=result.get("score", 3),
        difficulty=request.difficulty
    )
    db.add(session)
    db.commit()

    return {
        "score": result.get("score", 3),
        "feedback": result.get("feedback", ""),
        "corrected": result.get("corrected", request.user_attempt)
    }
