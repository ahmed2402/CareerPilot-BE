# router.py
import sys
import os
from fastapi import APIRouter
from .models import (
    ChatRequest, ChatResponse, 
    CreateSessionResponse, AllSessionsResponse, 
    DeleteSessionResponse, LoadChatHistoryResponse
)
from .sessions_store import create_session, list_sessions, delete_session,update_session_title,get_session
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from rag_core.retriever import get_full_conversational_chain, llm, get_redis_history

router = APIRouter()

DEFAULT_K = 5
conversation_chain = get_full_conversational_chain(llm, DEFAULT_K)


# -----------------------------------------
# 1) Create New Chat
# -----------------------------------------
@router.post("/session/new", response_model=CreateSessionResponse)
async def create_new_chat():
    session_meta = create_session("New Chat")
    return CreateSessionResponse(
        session_id=session_meta["session_id"],
        title=session_meta["title"],
        created_at=session_meta["created_at"]
    )


# -----------------------------------------
# 2) List All Sessions
# -----------------------------------------
@router.get("/sessions", response_model=AllSessionsResponse)
async def get_all_sessions():
    return AllSessionsResponse(sessions=list_sessions())


# -----------------------------------------
# 3) Load Chat History
# -----------------------------------------
@router.get("/session/{session_id}/history", response_model=LoadChatHistoryResponse)
async def load_chat_history(session_id: str):
    redis_history = get_redis_history(session_id)
    messages = redis_history.messages  # List[BaseMessage]

    formatted = []
    for msg in messages:
        # msg.type = "human" / "ai"
        formatted.append({
            "role": msg.type,
            "content": msg.content
        })

    return LoadChatHistoryResponse(
        session_id=session_id,
        messages=formatted
    )


# -----------------------------------------
# 4) Delete Chat Session
# -----------------------------------------
@router.delete("/session/{session_id}", response_model=DeleteSessionResponse)
async def delete_chat(session_id: str):
    redis_history = get_redis_history(session_id)
    redis_history.clear()

    return DeleteSessionResponse(
        success=delete_session(session_id)
    )


# -----------------------------------------
# 5) Chat Endpoint (RAG + Redis Memory)
# -----------------------------------------
@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    chain = conversation_chain

    if payload.k_retrieval != DEFAULT_K:
        chain = get_full_conversational_chain(llm, payload.k_retrieval)

    answer = chain.invoke(
        {"input": payload.message},
        config={"configurable": {"session_id": payload.session_id}}
    )
    
#  Check and update chat title with the first message if it's still the default "New Chat"
    session_meta = get_session(payload.session_id)
    if session_meta and session_meta.get("title") == "New Chat":
         # Take first 50 chars of the message for title
         update_session_title(payload.session_id, payload.message[:50])
 
    return ChatResponse(session_id=payload.session_id, answer=answer)
