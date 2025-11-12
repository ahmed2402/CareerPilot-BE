from pydantic import BaseModel
from typing import List, Dict

class ResumeMatchRequest(BaseModel):
    resume_text: str
    job_description: str

class ResumeMatchResponse(BaseModel):
    match_score: float
    insights: Dict
    output_pdf_path: str
