from pydantic import BaseModel
from typing import List, Dict

class InterviewPrepRequest(BaseModel):
    user_message: str
    session_id: str

class InterviewPrepResponse(BaseModel):
    ai_response: str
