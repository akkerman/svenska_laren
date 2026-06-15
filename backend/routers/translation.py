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

    prompt = f"""Je bent een Nederlands taalleraar die Zweeds-naar-Nederlands vertalingen beoordeelt.

TAAK:
1. Analyseer de originele zin in het {lang_src}
2. Vergelijk met de studentvertaling in het {lang_tgt}
3. Identificeer specifieke fouten (verkeerde woordkeuze, grammatica, volgorde)
4. Geef concrete feedback met voorbeelden
5. Geef de ideale vertaling (VOLLEDIG in het {lang_tgt}, geen {lang_src} woorden)

ORIGINEEL ({lang_src}): "{request.source_sentence}"
STUDENT POGING ({lang_tgt}): "{request.user_attempt}"
{difficulty_instr}

Antwoord in JSON met exact deze velden:
{{
  "score": <geheel getal 1-5>,
  "feedback": "<specific commentaar op wat goed/fout is in het Nederlands, met voorbeelden van foutieve en correcte woorden>",
  "corrected": "<de ideale vertaling, VOLLEDIG in het {lang_tgt}>"
}}

REGELS:
- Feedback moet altijd in het Nederlands zijn
- Noem SPECIFIEKE woorden uit de studentpoging die fout zijn
- Het 'corrected' veld: GEEN {lang_src} woorden! Alles in het {lang_tgt}
- Wees duidelijk welk {lang_src} woord welk {lang_tgt} woord zou moeten zijn"""

    system = f"""Je bent een ervaren taalleraar die Zweeds-naar-Nederlands vertalingen beoordeelt.

ANTWOORD REGELS:
- Antwoord ALLEEN in geldige JSON, niets anders
- Feedback ALTIJD in het Nederlands
- 'corrected' veld MOET volledig in het {lang_tgt} zijn
- Geen {lang_src} woorden in het corrected veld
- Zorg dat je antwoord geldig JSON is

FEEDBACK REGELS:
- Specifiek: noem welke woorden/zinsdelen fout zijn
- Constructief: leg uit wat beter kan
- Duidelijk: wees helder wat het verschil is tussen studentpoging en correcte versie
- Wees niet verwarrend door talen door elkaar te halen"""

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
