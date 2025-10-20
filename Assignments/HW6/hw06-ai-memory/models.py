from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

# Pydantic Models for API
class ChatRequest(BaseModel):
    user_id: str
    session_id: Optional[str] = "default"
    message: str

class ChatResponse(BaseModel):
    reply: str
    short_term_count: int
    long_term_summary: Optional[str] = None
    episodic_facts: List[str] = []

class MemoryResponse(BaseModel):
    messages: List[dict]
    session_summary: Optional[str] = None
    lifetime_summary: Optional[str] = None
    episodic_facts: List[dict]

class AggregateResponse(BaseModel):
    daily_counts: List[dict]
    recent_summaries: List[dict]