import os
import tempfile

from fastapi import APIRouter, HTTPException
from .models import ResumeMatchRequest, ResumeMatchResponse
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from workflows.resume_match_pipeline import app as resume_match_pipeline

router = APIRouter()

@router.post("/match", response_model=ResumeMatchResponse)
async def match_resume(request: ResumeMatchRequest):
    resume_file_path = None
    try:
        # Save resume text to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", mode="w+", encoding="utf-8") as temp_resume_file:
            temp_resume_file.write(request.resume_text)
            resume_file_path = temp_resume_file.name

        initial_state = {"resume_path": resume_file_path, "jd_text": request.job_description}
        final_state = {}
        for state in resume_match_pipeline.stream(initial_state):
            final_state.update(state)

        similarity_score = final_state.get("similarity_score", 0.0)
        insights = final_state.get("insights", {})
        output_pdf_path = final_state.get("output_pdf_path", "N/A")

        return ResumeMatchResponse(
            match_score=similarity_score,
            insights=insights,
            output_pdf_path=output_pdf_path
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up the temporary file
        if resume_file_path and os.path.exists(resume_file_path):
            os.remove(resume_file_path)
