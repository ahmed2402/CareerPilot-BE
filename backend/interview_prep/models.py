# models.py

from pydantic import BaseModel
from typing import List, Optional


class ChatRequest(BaseModel):
    session_id: str
    message: str
    k_retrieval: Optional[int] = None 


class ChatResponse(BaseModel):
    session_id: str
    answer: str


class CreateSessionResponse(BaseModel):
    session_id: str
    title: str
    created_at: int


class SessionItem(BaseModel):
    session_id: str
    title: str
    created_at: int


class AllSessionsResponse(BaseModel):
    sessions: List[SessionItem]


class DeleteSessionResponse(BaseModel):
    success: bool


class LoadChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[dict]  
