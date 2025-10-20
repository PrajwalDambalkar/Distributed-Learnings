import httpx
import numpy as np
from datetime import datetime
from typing import List, Optional, Dict
import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
CHAT_MODEL = os.getenv("CHAT_MODEL", "phi3:mini")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")
SHORT_TERM_N = int(os.getenv("SHORT_TERM_N", "10"))
SUMMARIZE_EVERY = int(os.getenv("SUMMARIZE_EVERY", "5"))


async def call_ollama_chat(messages: List[Dict[str, str]]) -> str:
    """Call Ollama chat API"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": CHAT_MODEL,
                "messages": messages,
                "stream": False
            }
        )
        result = response.json()
        return result["message"]["content"]


async def get_embedding(text: str) -> List[float]:
    """Get embedding from Ollama"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json={
                "model": EMBED_MODEL,
                "prompt": text
            }
        )
        result = response.json()
        return result["embedding"]


def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    a_np = np.array(a)
    b_np = np.array(b)
    return float(np.dot(a_np, b_np) / (np.linalg.norm(a_np) * np.linalg.norm(b_np)))


async def extract_facts(message: str) -> List[Dict]:
    """Extract facts from user message"""
    prompt = f"""Extract up to 3 important facts from this message that might be useful later.
For each fact, provide:
1. The fact (short sentence)
2. Importance score (0.0 to 1.0)

Message: {message}

Format your response as:
FACT: [fact text]
IMPORTANCE: [0.0-1.0]

(repeat for each fact, max 3)"""

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": CHAT_MODEL,
                "prompt": prompt,
                "stream": False
            }
        )
        result = response.json()
        text = result["response"]
    
    # Parse facts
    facts = []
    lines = text.split('\n')
    current_fact = None
    
    for line in lines:
        line = line.strip()
        if line.startswith("FACT:"):
            current_fact = line.replace("FACT:", "").strip()
        elif line.startswith("IMPORTANCE:") and current_fact:
            try:
                importance = float(line.replace("IMPORTANCE:", "").strip())
                importance = max(0.0, min(1.0, importance))  # Clamp to 0-1
                facts.append({"fact": current_fact, "importance": importance})
                current_fact = None
            except:
                pass
    
    # If parsing failed, create a simple fact
    if not facts and message:
        facts.append({"fact": message[:100], "importance": 0.5})
    
    return facts[:3]  # Max 3 facts


async def generate_summary(messages: List[Dict], summary_type: str = "session") -> str:
    """Generate summary from messages"""
    conversation = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
    
    prompt = f"""Summarize this conversation into 3-5 concise bullet points.
Focus on key topics, decisions, and important information.

Conversation:
{conversation}

Summary (bullet points):"""

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": CHAT_MODEL,
                "prompt": prompt,
                "stream": False
            }
        )
        result = response.json()
        return result["response"].strip()


async def retrieve_relevant_episodes(db, user_id: str, session_id: str, query_embedding: List[float], top_k: int = 3) -> List[Dict]:
    """Retrieve top-k relevant episodic memories"""
    episodes = []
    
    async for episode in db.episodes.find({
        "user_id": user_id,
        "session_id": session_id
    }):
        if "embedding" in episode and episode["embedding"]:
            similarity = cosine_similarity(query_embedding, episode["embedding"])
            episodes.append({
                "fact": episode["fact"],
                "importance": episode["importance"],
                "similarity": similarity
            })
    
    # Sort by similarity * importance
    episodes.sort(key=lambda x: x["similarity"] * x["importance"], reverse=True)
    return episodes[:top_k]


async def compose_prompt(
    db,
    user_id: str,
    session_id: str,
    current_message: str,
    short_term_messages: List[Dict],
    session_summary: Optional[str],
    lifetime_summary: Optional[str],
    episodic_facts: List[Dict]
) -> List[Dict[str, str]]:
    """Compose the full prompt with all memory types"""
    
    system_content = "You are a helpful AI assistant with memory of past conversations."
    
    # Add long-term summaries
    if lifetime_summary:
        system_content += f"\n\nUser Profile Summary:\n{lifetime_summary}"
    
    if session_summary:
        system_content += f"\n\nCurrent Session Summary:\n{session_summary}"
    
    # Add episodic facts
    if episodic_facts:
        facts_text = "\n".join([f"- {e['fact']}" for e in episodic_facts])
        system_content += f"\n\nRelevant Facts:\n{facts_text}"
    
    # Build messages array
    messages = [{"role": "system", "content": system_content}]
    
    # Add short-term messages
    for msg in short_term_messages:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    
    # Add current message
    messages.append({"role": "user", "content": current_message})
    
    return messages