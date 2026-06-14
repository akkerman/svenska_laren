from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database import get_db
from models import WordCard
from schemas import CardAnswerRequest, CardAnswerResponse

router = APIRouter(prefix="/api/cards", tags=["leitner"])

@router.post("/answer", response_model=CardAnswerResponse)
def answer_card(request: CardAnswerRequest, db: Session = Depends(get_db)):
    card = db.query(WordCard).filter(WordCard.id == request.card_id).first()
    if not card:
        raise ValueError("Card not found")

    today = datetime.now().date()

    if request.correct:
        card.box = min(card.box + 1, 5)
        card.total_correct += 1

        if card.box == 5:
            card.next_review = None
        else:
            days_delay = 2 ** (card.box - 1)
            card.next_review = today + timedelta(days=days_delay)
    else:
        card.box = 1
        card.total_wrong += 1
        card.next_review = today + timedelta(days=1)

    db.commit()
    db.refresh(card)

    return {
        "new_box": card.box,
        "next_review": card.next_review
    }
