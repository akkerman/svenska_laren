import json
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, UserSettings, WordCard

DATABASE_URL = "sqlite:///./svenska_laren.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if db.query(UserSettings).count() == 0:
            default_settings = UserSettings(id="local", difficulty=0.3)
            db.add(default_settings)
            db.commit()

        if db.query(WordCard).count() == 0:
            wordlist_path = os.path.join(os.path.dirname(__file__), "data", "wordlist_1000.json")
            with open(wordlist_path, "r", encoding="utf-8") as f:
                words = json.load(f)

            today = datetime.now().date()
            for word in words:
                # Create card for SE→NL
                card_se_nl = WordCard(
                    swedish=word["swedish"],
                    dutch=word["dutch"],
                    direction="se_nl",
                    box=1,
                    next_review=today,
                    total_correct=0,
                    total_wrong=0
                )
                db.add(card_se_nl)

                # Create card for NL→SE
                card_nl_se = WordCard(
                    swedish=word["swedish"],
                    dutch=word["dutch"],
                    direction="nl_se",
                    box=1,
                    next_review=today,
                    total_correct=0,
                    total_wrong=0
                )
                db.add(card_nl_se)
            db.commit()
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
