from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import UserSettings
from schemas import SettingsResponse, SettingsUpdate

router = APIRouter(prefix="/api/settings", tags=["settings"])

@router.get("", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    settings = db.query(UserSettings).filter(UserSettings.id == "local").first()
    if not settings:
        settings = UserSettings(id="local", difficulty=0.3)
        db.add(settings)
        db.commit()
    return {"difficulty": settings.difficulty}

@router.put("", response_model=SettingsResponse)
def update_settings(update: SettingsUpdate, db: Session = Depends(get_db)):
    settings = db.query(UserSettings).filter(UserSettings.id == "local").first()
    if not settings:
        settings = UserSettings(id="local")
        db.add(settings)

    settings.difficulty = update.difficulty
    db.commit()
    db.refresh(settings)
    return {"difficulty": settings.difficulty}
