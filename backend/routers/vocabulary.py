from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
import random
from database import get_db
from models import WordCard, UserSettings
from schemas import WordCardResponse, WordCardCreate, CardStatsResponse

router = APIRouter(prefix="/api/cards", tags=["vocabulary"])

def normalize_search(text: str) -> str:
    """Remove Swedish diacritics for search comparison."""
    replacements = {
        'å': 'a', 'ä': 'a',
        'ö': 'o'
    }
    return ''.join(replacements.get(c, c) for c in text.lower())

def get_frequency_limit(difficulty: float):
    """Convert difficulty (0-1) to max frequency rank.
    difficulty is multiplied by max frequency rank in dataset.
    difficulty 0.3 → 30% of words, 1.0 → all words
    """
    max_frequency_rank = 1587  # Highest frequency rank in dataset
    if difficulty >= 1.0:
        return max_frequency_rank + 1
    return max(100, int(difficulty * max_frequency_rank))

def get_weighted_wordlist(direction: str, db: Session):
    """Get wordlist weighted by learning progress.
    Box 1-2 (learning): weight 3x
    Box 3-5 (known): weight 1x
    Returns list of dicts with swedish, dutch, box, priority
    """
    settings = db.query(UserSettings).filter(UserSettings.id == "local").first()
    difficulty = settings.difficulty if settings else 0.3
    max_frequency = get_frequency_limit(difficulty)

    words = db.query(WordCard).filter(
        WordCard.direction == direction,
        WordCard.frequency_rank <= max_frequency
    ).all()

    weighted_list = []
    for word in words:
        priority = word.box <= 2
        weight = 3 if priority else 1

        word_dict = {
            "swedish": word.swedish,
            "dutch": word.dutch,
            "box": word.box,
            "priority": priority
        }

        for _ in range(weight):
            weighted_list.append(word_dict)

    return weighted_list

@router.get("/due", response_model=list[WordCardResponse])
def get_due_cards(direction: str = Query("se_nl"), db: Session = Depends(get_db)):
    today = datetime.now().date()

    # Get user's difficulty setting
    settings = db.query(UserSettings).filter(UserSettings.id == "local").first()
    difficulty = settings.difficulty if settings else 0.3

    # Determine max frequency rank to show
    max_frequency = get_frequency_limit(difficulty)

    # Get all due cards for specified direction, filtered by frequency
    due = db.query(WordCard).filter(
        WordCard.direction == direction,
        WordCard.frequency_rank <= max_frequency,
        (WordCard.next_review <= today) | (WordCard.next_review.is_(None))
    ).all()
    random.shuffle(due)
    return due

@router.get("/stats", response_model=CardStatsResponse)
def get_stats(direction: str = Query("se_nl"), db: Session = Depends(get_db)):
    # Get user's difficulty setting
    settings = db.query(UserSettings).filter(UserSettings.id == "local").first()
    difficulty = settings.difficulty if settings else 0.3

    # Determine max frequency rank to show
    max_frequency = get_frequency_limit(difficulty)

    # Count filtered (by difficulty) and total
    total = db.query(WordCard).filter(
        WordCard.direction == direction,
        WordCard.frequency_rank <= max_frequency
    ).count()
    mastered = db.query(WordCard).filter(
        WordCard.direction == direction,
        WordCard.frequency_rank <= max_frequency,
        WordCard.box == 5
    ).count()

    per_box = []
    for box_num in range(1, 6):
        filtered = db.query(WordCard).filter(
            WordCard.direction == direction,
            WordCard.frequency_rank <= max_frequency,
            WordCard.box == box_num
        ).count()
        total_in_box = db.query(WordCard).filter(
            WordCard.direction == direction,
            WordCard.box == box_num
        ).count()
        per_box.append({"filtered": filtered, "total": total_in_box})

    return {
        "total": total,
        "mastered": mastered,
        "per_box": per_box
    }

@router.patch("/{card_id}/notes")
def update_card_notes(card_id: int, notes: str = Query(""), db: Session = Depends(get_db)):
    """Update notes for a card."""
    card = db.query(WordCard).filter(WordCard.id == card_id).first()
    if not card:
        raise ValueError("Card not found")

    card.notes = notes if notes else None
    db.commit()
    db.refresh(card)
    return {"status": "updated", "card_id": card_id, "notes": card.notes}

@router.post("", response_model=WordCardResponse)
def add_custom_word(word: WordCardCreate, db: Session = Depends(get_db)):
    today = datetime.now().date()
    new_card = WordCard(
        swedish=word.swedish,
        dutch=word.dutch,
        box=1,
        next_review=today
    )
    db.add(new_card)
    db.commit()
    db.refresh(new_card)
    return new_card

@router.post("/sync/wordlist")
def sync_wordlist_from_file(db: Session = Depends(get_db)):
    """Add missing words from wordlist file without affecting existing progress."""
    import json
    import os

    wordlist_path = os.path.join(os.path.dirname(__file__), "../data/wordlist_1000.json")
    with open(wordlist_path, "r", encoding="utf-8") as f:
        words = json.load(f)

    # Get existing Swedish words (both directions) to avoid duplicates
    existing_words = {
        card.swedish for card in db.query(WordCard.swedish).filter(
            WordCard.direction == "se_nl"
        ).all()
    }

    today = datetime.now().date()
    added_count = 0

    for word in words:
        if word["swedish"] not in existing_words:
            # Add for SE→NL
            card_se_nl = WordCard(
                swedish=word["swedish"],
                dutch=word["dutch"],
                frequency_rank=word.get("frequency_rank", 1000),
                direction="se_nl",
                box=1,
                next_review=today,
                total_correct=0,
                total_wrong=0
            )
            db.add(card_se_nl)

            # Add for NL→SE
            card_nl_se = WordCard(
                swedish=word["swedish"],
                dutch=word["dutch"],
                frequency_rank=word.get("frequency_rank", 1000),
                direction="nl_se",
                box=1,
                next_review=today,
                total_correct=0,
                total_wrong=0
            )
            db.add(card_nl_se)
            added_count += 2

    db.commit()

    return {
        "status": "synced",
        "added": added_count,
        "total_words": db.query(WordCard).count()
    }

@router.get("/search", response_model=list[WordCardResponse])
def search_cards(q: str = Query(""), db: Session = Depends(get_db)):
    import re

    if not q or len(q.strip()) < 2:
        return []

    q = q.lower()

    # Generate search variations: a→[a,å,ä], o→[o,ö]
    variations = [q]
    if 'a' in q:
        variations.append(q.replace('a', 'å'))
        variations.append(q.replace('a', 'ä'))
    if 'o' in q:
        variations.append(q.replace('o', 'ö'))

    # Build regex: match any variation
    pattern = '|'.join(re.escape(v) for v in variations)
    regex = re.compile(pattern, re.IGNORECASE)

    # Query both directions
    all_cards = db.query(WordCard).all()
    results_with_score = []
    seen = set()

    for card in all_cards:
        # Keep separate entries for each direction
        key = (card.id, card.direction)
        if key in seen:
            continue
        seen.add(key)

        swedish_match = regex.search(card.swedish)
        dutch_match = regex.search(card.dutch)

        if swedish_match or dutch_match:
            # Score: exact match = 0, contains = 1
            if swedish_match:
                score = 0 if card.swedish.lower() == q else 1
            elif dutch_match:
                score = 0 if card.dutch.lower() == q else 1
            else:
                score = 2

            results_with_score.append((card, score))

    # Sort: by score (exact matches first)
    results_with_score.sort(key=lambda x: x[1])
    return [card for card, _ in results_with_score]
