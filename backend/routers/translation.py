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
import random

router = APIRouter(prefix="/api/translation", tags=["translation"])

TOPICS = [
    "family", "food", "travel", "work", "hobbies", "shopping",
    "weather", "sports", "animals", "school", "home", "health"
]

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
    topic = request.topic or random.choice(TOPICS)
    topic_str = f"Topic: {topic}."

    # Get weighted wordlist for context
    direction = "nl_se" if is_nl_to_se else "se_nl"
    wordlist = get_weighted_wordlist(direction, db)
    wordlist_str = json.dumps(wordlist[:50])  # Limit to 50 words

    exclude_note = ""
    if request.exclude_sentence:
        exclude_note = f"\n\nDO NOT generate this sentence (it was just used): {request.exclude_sentence}"

    if is_nl_to_se:
        prompt = f"""{difficulty_instr} {topic_str}

Generate ONE sentence pair. The sentence must be in DUTCH.{exclude_note}

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

Generate ONE sentence pair. The sentence must be in SWEDISH.{exclude_note}

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

    import re
    sentence = ""
    translation = ""
    max_retries = 3

    for attempt in range(max_retries):
        response_text = ollama.generate(prompt, system)
        print(f"[TRANSLATION] Direction: {request.direction}, Attempt: {attempt + 1}/{max_retries}")
        print(f"[TRANSLATION] AI Response: {response_text}")

        try:
            # Extract JSON from response (may contain markdown or explanation)
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

            if sentence and translation:
                # Check if excluded sentence
                if request.exclude_sentence and sentence.strip().lower() == request.exclude_sentence.strip().lower():
                    print(f"[TRANSLATION] Generated excluded sentence on attempt {attempt + 1}, retrying...")
                    sentence = ""
                    translation = ""
                    continue

                print(f"[TRANSLATION] Success on attempt {attempt + 1}")
                break

        except (json.JSONDecodeError, AttributeError, TypeError, ValueError):
            print(f"[TRANSLATION ERROR] Failed to parse on attempt {attempt + 1}: {response_text}")
            if attempt == max_retries - 1:
                print(f"[TRANSLATION ERROR] Max retries ({max_retries}) reached, giving up")

    return {
        "sentence": sentence,
        "language_from": lang_from,
        "language_to": lang_to,
        "correct_translation": translation
    }

@router.post("/evaluate", response_model=TranslationEvaluateResponse)
def evaluate_translation(request: TranslationEvaluateRequest, db: Session = Depends(get_db)):
    is_nl_to_se = request.direction == "nl_to_se"
    lang_from = "Dutch" if is_nl_to_se else "Swedish"
    lang_to = "Swedish" if is_nl_to_se else "Dutch"

    def normalize(s: str) -> str:
        return s.strip().rstrip(".!?").strip().lower()

    if normalize(request.user_attempt) == normalize(request.correct_translation):
        feedback = "Uitstekend! Je vertaling is precies goed."
        print(f"[EVALUATE] Exact match, skipping AI feedback")
    else:
        lang_from_nl = "Zweeds" if lang_from == "Swedish" else "Nederlands"
        lang_to_nl = "Nederlands" if lang_to == "Dutch" else "Zweeds"

        prompt = f"""
De student vertaalde de zin "{request.source_sentence}" ({lang_from_nl}) naar "{request.user_attempt}" ({lang_to_nl}). De verwachte vertaling is  "{request.correct_translation}" ({lang_to_nl}).
Beoordeel ALLEEN de {lang_to_nl} vertaling van de student. Geef aan of de vertaling klopt, wat er afwijkt van de verwachte vertaling, en of de afwijking acceptabel is. 
Verzin geen andere zinnen. Wees precies en bondig. Maximaal 2 zinnen."""

        system = "Je bent een taaldocent die feedback geeft op een vertaaloefening. Spreek de student altijd direct aan met 'je'. Reageer altijd in het Nederlands."

        print(f"[EVALUATE] Prompt: {prompt}")
        feedback = ollama.generate(prompt, system)
        print(f"[EVALUATE] Feedback: {feedback}")

    session = TranslationSession(
        direction=request.direction,
        source_sentence=request.source_sentence,
        user_attempt=request.user_attempt,
        llm_feedback=feedback,
        score=0,
        difficulty=request.difficulty
    )
    db.add(session)
    db.commit()

    return {
        "source_sentence": request.source_sentence,
        "user_attempt": request.user_attempt,
        "correct_translation": request.correct_translation,
        "feedback": feedback,
    }
