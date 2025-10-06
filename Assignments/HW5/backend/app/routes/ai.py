from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import httpx
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/ai", tags=["AI Chat"])

async def call_ollama(messages: List[dict]) -> str:
    """Call Ollama API with conversation history"""
    url = "http://localhost:11434/api/chat"
    
    payload = {
        "model": "llama3.1",
        "messages": messages,
        "stream": False
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")

@router.post("/chat", response_model=schemas.ChatOut)
async def chat(chat_input: schemas.ChatIn, db: Session = Depends(get_db)):
    """Send message and get AI response"""
    
    # Get or create conversation
    if chat_input.conversation_id:
        conversation = db.query(models.Conversation).filter(
            models.Conversation.id == chat_input.conversation_id
        ).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        # Create new conversation
        conversation = models.Conversation(
            user_id=chat_input.user_id,
            title=chat_input.title or f"Chat {chat_input.message[:30]}..."
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    # Save user message
    user_message = models.Message(
        conversation_id=conversation.id,
        role=models.MessageRole.user,
        content=chat_input.message
    )
    db.add(user_message)
    db.commit()
    
    # Get conversation history for context
    messages = db.query(models.Message).filter(
        models.Message.conversation_id == conversation.id
    ).order_by(models.Message.created_at).all()
    
    # Format for Ollama
    ollama_messages = [
        {"role": msg.role.value, "content": msg.content}
        for msg in messages
    ]
    
    # Call Ollama
    ai_response = await call_ollama(ollama_messages)
    
    # Save assistant response
    assistant_message = models.Message(
        conversation_id=conversation.id,
        role=models.MessageRole.assistant,
        content=ai_response
    )
    db.add(assistant_message)
    db.commit()
    
    return schemas.ChatOut(
        conversation_id=conversation.id,
        reply=ai_response
    )

@router.get("/conversations", response_model=List[schemas.ConversationOut])
def get_conversations(user_id: int = 1, db: Session = Depends(get_db)):
    """Get all conversations for a user"""
    conversations = db.query(models.Conversation).filter(
        models.Conversation.user_id == user_id
    ).order_by(models.Conversation.updated_at.desc()).all()
    
    return conversations

@router.get("/messages/{conversation_id}", response_model=List[schemas.MessageOut])
def get_messages(conversation_id: int, db: Session = Depends(get_db)):
    """Get all messages in a conversation"""
    conversation = db.query(models.Conversation).filter(
        models.Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = db.query(models.Message).filter(
        models.Message.conversation_id == conversation_id
    ).order_by(models.Message.created_at).all()
    
    return messages