from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models import WordCard
from schemas import WordCardResponse, WordCardCreate, CardStatsResponse

router = APIRouter(prefix="/api/cards", tags=["vocabulary"])

@router.get("/due", response_model=list[WordCardResponse])
def get_due_cards(db: Session = Depends(get_db)):
    today = datetime.now().date()
    due = db.query(WordCard).filter(
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
