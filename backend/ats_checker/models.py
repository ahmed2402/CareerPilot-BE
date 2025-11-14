from pydantic import BaseModel
from typing import List, Dict

class   AtsCheckRequest(BaseModel):
    resume_text: str
    job_description: str | None = None

class CategoryScore(BaseModel):
    score: float
    weight: float
    weighted_score: float

class AtsCheckResponse(BaseModel):
    overall_score: float
    category_scores: Dict[str, CategoryScore]
    recommendations: List[str]
