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

            for word in words:
                card = WordCard(
                    swedish=word["swedish"],
                    english=word["english"],
                    category=word.get("category", "other"),
                    box=1,
                    next_review=datetime.now().date(),
                    total_correct=0,
                    total_wrong=0
                )
                db.add(card)
            db.commit()
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
