"""FastAPI backend for Arsenic Awareness Chatbot."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.chatbot import ArsenicChatbot
from core.utils.validators import sanitize_input

app = FastAPI(title="Arsenic Awareness Chatbot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chatbot = ArsenicChatbot()


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    response: str
    language: str
    sources: List[dict]


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Chat endpoint."""
    message = sanitize_input(request.message)
    if not message:
        raise HTTPException(status_code=400, detail="Invalid message")
    try:
        result = chatbot.chat(message, session_id=request.session_id or "default")
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
