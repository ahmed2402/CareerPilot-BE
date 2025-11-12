from pydantic import BaseModel
from typing import List, Dict, Optional

class QuestionGenerateRequest(BaseModel):
    job_description: str
    num_questions: int = 5
    question_types: Optional[List[str]] = None

class Question(BaseModel):
    question: str
    type: str
    difficulty: str
    focus_area: str
    ideal_answer_keywords: List[str]

class QuestionGenerateResponse(BaseModel):
    questions: List[Question]

class AnalyzeResponseRequest(BaseModel):
    transcript: Optional[str] = None
    audio_base64: Optional[str] = None  # Base64 encoded audio bytes
    question: str
    job_description: Optional[str] = None
    include_audio_analysis: bool = False
    include_sentiment_analysis: bool = False

class ScoreDetail(BaseModel):
    score: float
    details: Optional[str] = None
    # Add any other specific fields from the analysis output

class OverallScoreDetail(ScoreDetail):
    grade: str
    percentage: float

class AnalysisResult(BaseModel):
    overall_score: OverallScoreDetail
    clarity: ScoreDetail
    confidence: ScoreDetail
    fluency: ScoreDetail
    relevance: ScoreDetail
    sentiment: ScoreDetail
    keyword_match: ScoreDetail

class AnalyzeResponseResponse(BaseModel):
    analysis: AnalysisResult
    feedback: str

class ReportGenerateRequest(BaseModel):
    interview_session: Dict  # This will be a complex dict mirroring the UI's session state
    job_description: Optional[str] = None

class ReportGenerateResponse(BaseModel):
    report_data: Dict  # This will be the comprehensive report dictionary
    text_report: str
