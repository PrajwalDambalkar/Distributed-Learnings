from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import List
import os
from dotenv import load_dotenv

from models import ChatRequest, ChatResponse, MemoryResponse, AggregateResponse
from memory import (
    call_ollama_chat,
    get_embedding,
    extract_facts,
    generate_summary,
    retrieve_relevant_episodes,
    compose_prompt,
    SHORT_TERM_N,
    SUMMARIZE_EVERY
)

load_dotenv()

app = FastAPI(title="AI Memory System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hw06_db")
client = AsyncIOMotorClient(MONGODB_URI)
db = client.hw06_db


@app.on_event("startup")
async def startup_db():
    print("✅ Connected to MongoDB")


@app.on_event("shutdown")
async def shutdown_db():
    client.close()


@app.get("/")
async def root():
    return {"message": "AI Memory System API"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint with memory"""
    
    user_id = request.user_id
    session_id = request.session_id or "default"
    message = request.message
    
    # 1. Save user message
    user_msg = {
        "user_id": user_id,
        "session_id": session_id,
        "role": "user",
        "content": message,
        "created_at": datetime.utcnow()
    }
    await db.messages.insert_one(user_msg)
    
    # 2. Get short-term memory (last N messages)
    short_term = []
    async for msg in db.messages.find({
        "user_id": user_id,
        "session_id": session_id
    }).sort("created_at", -1).limit(SHORT_TERM_N):
        short_term.append(msg)
    short_term.reverse()  # Chronological order
    
    # 3. Get long-term summaries
    session_summary_doc = await db.summaries.find_one({
        "user_id": user_id,
        "session_id": session_id,
        "scope": "session"
    }, sort=[("created_at", -1)])
    
    lifetime_summary_doc = await db.summaries.find_one({
        "user_id": user_id,
        "session_id": None,
        "scope": "user"
    }, sort=[("created_at", -1)])
    
    session_summary = session_summary_doc["text"] if session_summary_doc else None
    lifetime_summary = lifetime_summary_doc["text"] if lifetime_summary_doc else None
    
    # 4. Extract and save episodic facts from user message
    facts = await extract_facts(message)
    message_embedding = await get_embedding(message)
    
    for fact_data in facts:
        fact_embedding = await get_embedding(fact_data["fact"])
        episode = {
            "user_id": user_id,
            "session_id": session_id,
            "fact": fact_data["fact"],
            "importance": fact_data["importance"],
            "embedding": fact_embedding,
            "created_at": datetime.utcnow()
        }
        await db.episodes.insert_one(episode)
    
    # 5. Retrieve relevant episodic memories
    relevant_episodes = await retrieve_relevant_episodes(
        db, user_id, session_id, message_embedding, top_k=3
    )
    
    # 6. Compose prompt with all memory types
    prompt_messages = await compose_prompt(
        db, user_id, session_id, message,
        short_term, session_summary, lifetime_summary, relevant_episodes
    )
    
    # 7. Call Ollama chat
    assistant_reply = await call_ollama_chat(prompt_messages)
    
    # 8. Save assistant message
    assistant_msg = {
        "user_id": user_id,
        "session_id": session_id,
        "role": "assistant",
        "content": assistant_reply,
        "created_at": datetime.utcnow()
    }
    await db.messages.insert_one(assistant_msg)
    
    # 9. Check if we need to summarize
    user_msg_count = await db.messages.count_documents({
        "user_id": user_id,
        "session_id": session_id,
        "role": "user"
    })
    
    if user_msg_count % SUMMARIZE_EVERY == 0:
        # Generate session summary
        recent_msgs = []
        async for msg in db.messages.find({
            "user_id": user_id,
            "session_id": session_id
        }).sort("created_at", -1).limit(SUMMARIZE_EVERY * 2):
            recent_msgs.append(msg)
        recent_msgs.reverse()
        
        summary_text = await generate_summary(recent_msgs, "session")
        
        await db.summaries.insert_one({
            "user_id": user_id,
            "session_id": session_id,
            "scope": "session",
            "text": summary_text,
            "created_at": datetime.utcnow()
        })
        
        # Update lifetime summary every 3 session summaries
        session_summary_count = await db.summaries.count_documents({
            "user_id": user_id,
            "scope": "session"
        })
        
        if session_summary_count % 3 == 0:
            all_summaries = []
            async for s in db.summaries.find({
                "user_id": user_id,
                "scope": "session"
            }).sort("created_at", -1).limit(5):
                all_summaries.append(s)
            
            if all_summaries:
                combined = "\n\n".join([s["text"] for s in all_summaries])
                lifetime_text = await generate_summary(
                    [{"role": "user", "content": combined}],
                    "user"
                )
                
                await db.summaries.insert_one({
                    "user_id": user_id,
                    "session_id": None,
                    "scope": "user",
                    "text": lifetime_text,
                    "created_at": datetime.utcnow()
                })
    
    # 10. Return response
    return ChatResponse(
        reply=assistant_reply,
        short_term_count=len(short_term),
        long_term_summary=session_summary or lifetime_summary,
        episodic_facts=[e["fact"] for e in relevant_episodes]
    )


@app.get("/api/memory/{user_id}", response_model=MemoryResponse)
async def get_memory(user_id: str, session_id: str = "default"):
    """Get memory view for a user"""
    
    # Last 16 messages
    messages = []
    async for msg in db.messages.find({
        "user_id": user_id,
        "session_id": session_id
    }).sort("created_at", -1).limit(16):
        messages.append({
            "role": msg["role"],
            "content": msg["content"],
            "created_at": msg["created_at"].isoformat()
        })
    messages.reverse()
    
    # Latest summaries
    session_summary_doc = await db.summaries.find_one({
        "user_id": user_id,
        "session_id": session_id,
        "scope": "session"
    }, sort=[("created_at", -1)])
    
    lifetime_summary_doc = await db.summaries.find_one({
        "user_id": user_id,
        "session_id": None,
        "scope": "user"
    }, sort=[("created_at", -1)])
    
    # Last 20 episodic facts
    episodes = []
    async for ep in db.episodes.find({
        "user_id": user_id,
        "session_id": session_id
    }).sort("created_at", -1).limit(20):
        episodes.append({
            "fact": ep["fact"],
            "importance": ep["importance"],
            "created_at": ep["created_at"].isoformat()
        })
    
    return MemoryResponse(
        messages=messages,
        session_summary=session_summary_doc["text"] if session_summary_doc else None,
        lifetime_summary=lifetime_summary_doc["text"] if lifetime_summary_doc else None,
        episodic_facts=episodes
    )


@app.get("/api/aggregate/{user_id}", response_model=AggregateResponse)
async def get_aggregate(user_id: str):
    """Get aggregate statistics"""
    
    # Daily message counts
    pipeline = [
        {"$match": {"user_id": user_id}},
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$created_at"
                    }
                },
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id": -1}},
        {"$limit": 30}
    ]
    
    daily_counts = []
    async for doc in db.messages.aggregate(pipeline):
        daily_counts.append({
            "date": doc["_id"],
            "count": doc["count"]
        })
    
    # Recent summaries
    summaries = []
    async for s in db.summaries.find({
        "user_id": user_id
    }).sort("created_at", -1).limit(5):
        summaries.append({
            "scope": s["scope"],
            "text": s["text"],
            "created_at": s["created_at"].isoformat()
        })
    
    return AggregateResponse(
        daily_counts=daily_counts,
        recent_summaries=summaries
    )