from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models import WordCard, UserSettings
from schemas import WordCardResponse, WordCardCreate, CardStatsResponse

router = APIRouter(prefix="/api/cards", tags=["vocabulary"])

def get_difficulty_filters(difficulty: float):
    """Return which boxes to include based on difficulty level."""
    if difficulty < 0.3:
        return [1, 2]
    elif difficulty < 0.6:
        return [1, 2, 3, 4]
    else:
        return [1, 2, 3, 4, 5]

@router.get("/due", response_model=list[WordCardResponse])
def get_due_cards(db: Session = Depends(get_db)):
    today = datetime.now().date()

    # Get user's difficulty setting
    settings = db.query(UserSettings).filter(UserSettings.id == "local").first()
    difficulty = settings.difficulty if settings else 0.3

    # Determine which boxes to show
    boxes_to_show = get_difficulty_filters(difficulty)

    # Get due cards from allowed boxes
    due = db.query(WordCard).filter(
        WordCard.box.in_(boxes_to_show),
        (WordCard.next_review <= today) | (WordCard.next_review.is_(None))
    ).all()
    return due

@router.get("/stats", response_model=CardStatsResponse)
def get_stats(db: Session = Depends(get_db)):
    total = db.query(WordCard).count()
    mastered = db.query(WordCard).filter(WordCard.box == 5).count()

    per_box = []
    for box_num in range(1, 6):
        count = db.query(WordCard).filter(WordCard.box == box_num).count()
        per_box.append(count)

    return {
        "total": total,
        "mastered": mastered,
        "per_box": per_box
    }

@router.post("", response_model=WordCardResponse)
def add_custom_word(word: WordCardCreate, db: Session = Depends(get_db)):
    today = datetime.now().date()
    new_card = WordCard(
        swedish=word.swedish,
        english=word.english,
        category=word.category or "custom",
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

    # Get existing Swedish words to avoid duplicates
    existing_words = {card.swedish for card in db.query(WordCard.swedish).all()}

    today = datetime.now().date()
    added_count = 0

    for word in words:
        if word["swedish"] not in existing_words:
            card = WordCard(
                swedish=word["swedish"],
                english=word["english"],
                category=word.get("category", "other"),
                box=1,
                next_review=today,
                total_correct=0,
                total_wrong=0
            )
            db.add(card)
            added_count += 1

    db.commit()

    return {
        "status": "synced",
        "added": added_count,
        "total_words": db.query(WordCard).count()
    }
