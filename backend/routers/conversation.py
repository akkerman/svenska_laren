from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
from models import ConversationMessage
from schemas import (
    ConversationStartRequest, ConversationStartResponse,
    ConversationMessageRequest, MessageResponse
)
from .vocabulary import get_weighted_wordlist
import ollama
import uuid
from datetime import datetime
import json

router = APIRouter(prefix="/api/conversation", tags=["conversation"])

DIFFICULTY_BEHAVIORS = {
    "low": "Respond in simple Swedish, offer English translations in parentheses, speak slowly with short sentences.",
    "medium": "Respond in Swedish, offer hints in English if stuck, moderate complexity.",
    "high": "Respond fully in Swedish, only correct significant errors.",
    "advanced": "Respond naturally like a native speaker, correct all errors including stylistic ones."
}

def get_difficulty_behavior(difficulty: float) -> str:
    if difficulty < 0.25:
        return DIFFICULTY_BEHAVIORS["low"]
    elif difficulty < 0.5:
        return DIFFICULTY_BEHAVIORS["medium"]
    elif difficulty < 0.75:
        return DIFFICULTY_BEHAVIORS["high"]
    else:
        return DIFFICULTY_BEHAVIORS["advanced"]

@router.post("/start", response_model=ConversationStartResponse)
def start_conversation(request: ConversationStartRequest, db: Session = Depends(get_db)):
    session_id = str(uuid.uuid4())
    behavior = get_difficulty_behavior(request.difficulty)

    # Get weighted wordlist for context
    wordlist = get_weighted_wordlist("se_nl", db)
    wordlist_str = json.dumps(wordlist[:100])  # Limit to 100 words for token efficiency

    system_prompt = f"""You are a friendly Swedish conversation partner. Topic: {request.topic}.
{behavior}

PREFERRED VOCABULARY (prioritize marked words):
{wordlist_str}

Use especially the words marked with "priority": true. You may use other words if needed for natural conversation.

IMPORTANT RULES:
- Keep your response short: max 2-3 sentences per reply
- Ask only ONE specific, directed question at a time
- Do NOT ask multiple questions in the same response
- Do NOT offer help or suggest what topics you can discuss ("I can help you with..." or "We could discuss...")
- Have a natural conversation like you're talking to a friend - just ask follow-up questions based on what they say

After your reply, if the user made any grammar or vocabulary errors, add a short "Correction:" section in English pointing out the mistake and the correct form. If there are no errors, do not add a Correction section."""

    initial_msg = {
        "role": "user",
        "content": f"Let's start a conversation about {request.topic} in Swedish. I'm a learner."
    }

    response_text = ollama.chat([initial_msg], system_prompt)

    user_msg = ConversationMessage(session_id=session_id, role="user", content=initial_msg["content"])
    assistant_msg = ConversationMessage(session_id=session_id, role="assistant", content=response_text)
    db.add(user_msg)
    db.add(assistant_msg)
    db.commit()

    return {
        "session_id": session_id,
        "opening_message": response_text
    }

@router.post("/message")
def stream_message(request: ConversationMessageRequest, db: Session = Depends(get_db)):
    history = db.query(ConversationMessage).filter(
        ConversationMessage.session_id == request.session_id
    ).order_by(ConversationMessage.created_at).all()

    messages = [{"role": msg.role, "content": msg.content} for msg in history]
    messages.append({"role": "user", "content": request.user_message})

    user_msg = ConversationMessage(session_id=request.session_id, role="user", content=request.user_message)
    db.add(user_msg)
    db.commit()

    behavior = get_difficulty_behavior(request.difficulty)

    # Get weighted wordlist for context
    wordlist = get_weighted_wordlist("se_nl", db)
    wordlist_str = json.dumps(wordlist[:100])  # Limit to 100 words for token efficiency

    system_prompt = f"""You are a friendly Swedish conversation partner.
{behavior}

PREFERRED VOCABULARY (prioritize marked words):
{wordlist_str}

Use especially the words marked with "priority": true. You may use other words if needed for natural conversation.

IMPORTANT RULES:
- Keep your response short: max 2-3 sentences per reply
- Ask only ONE specific, directed question at a time
- Do NOT ask multiple questions in the same response
- Do NOT offer help or suggest what topics you can discuss ("I can help you with..." or "We could discuss...")
- Have a natural conversation like you're talking to a friend - just ask follow-up questions based on what they say

After your reply, if the user made any grammar or vocabulary errors, add a short "Correction:" section in English pointing out the mistake and the correct form. If there are no errors, do not add a Correction section."""

    def generate():
        full_response = ""
        for chunk in ollama.stream_chat(messages, system_prompt):
            full_response += chunk
            yield f"data: {json.dumps({'token': chunk})}\n\n"

        assistant_msg = ConversationMessage(session_id=request.session_id, role="assistant", content=full_response)
        db.add(assistant_msg)
        db.commit()

    return StreamingResponse(generate(), media_type="text/event-stream")

@router.get("/history/{session_id}", response_model=list[MessageResponse])
def get_history(session_id: str, db: Session = Depends(get_db)):
    messages = db.query(ConversationMessage).filter(
        ConversationMessage.session_id == session_id
    ).order_by(ConversationMessage.created_at).all()
    return messages

@router.delete("/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    db.query(ConversationMessage).filter(
        ConversationMessage.session_id == session_id
    ).delete()
    db.commit()
    return {"status": "deleted"}
