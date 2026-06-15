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

ORIGINEEL (Zweeds): {request.source_sentence}
STUDENT VERTALING (Nederlands): {request.user_attempt}

STAP 1: Is de vertaling CORRECT?
- Kijk of alle woorden juist vertaald zijn
- Kijk of de zinsstructuur klopt
- Kijk of de betekenis hetzelfde is

STAP 2: Bepaal score en feedback
- Score 5: vertaling is perfect, geen fouten
  → feedback: "Perfect vertaald!"
  → corrected: dezelfde als student vertaling
- Score 4: bijna goed, kleine fout
  → feedback: alleen de specifieke fout noemen
  → corrected: verbeterde versie
- Score 3 of lager: meerdere fouten of fout concept
  → feedback: alle fouten specificeren
  → corrected: verbeterde versie

ANTWOORD IN DEZE JSON (meer niets):
{{
  "score": <1-5>,
  "feedback": "<Alleen als score < 5: wat is fout? Anders: 'Perfect vertaald!'>",
  "corrected": "<De vertaling (dezelfde als student als score=5, anders verbeterd)>"
}}

REGEL: Geef GEEN feedback over iets beter kan als de vertaling al perfect is!"""

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
