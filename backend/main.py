from fastapi import FastAPI
from backend.resume_matcher.router import router as resume_matcher_router
from backend.ats_checker.router import router as ats_checker_router
from backend.interview_prep.router import router as interview_prep_router
from backend.mock_interview.router import router as mock_interview_router

app = FastAPI()

app.include_router(resume_matcher_router, prefix="/resume-matcher", tags=["resume_matcher"])
app.include_router(ats_checker_router, prefix="/ats-checker", tags=["ats_checker"])
app.include_router(interview_prep_router, prefix="/interview-prep", tags=["interview_prep"])
app.include_router(mock_interview_router, prefix="/mock-interview", tags=["mock_interview"])

@app.get("/ping")
async def ping():
    return {"message": "pong"}
