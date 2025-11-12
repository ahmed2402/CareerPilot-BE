import os
import tempfile

from fastapi import APIRouter, HTTPException
from .models import AtsCheckRequest, AtsCheckResponse
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from workflows.ats_flow import ats_analysis_flow

router = APIRouter()

@router.post("/check", response_model=AtsCheckResponse)
async def check_ats(request: AtsCheckRequest):
    resume_file_path = None
    try:
        # Save resume text to a temporary file
        # Determine the correct suffix based on resume_text content if possible, or default to .pdf
        # For now, let's assume it's text that can be saved as .txt or .pdf source for processing
        # The ats_flow expects a path to a PDF/DOCX. Since we're getting text, we need to adapt.
        # For now, I will save it as a .txt and the ATSAnalyzer will need to be updated to handle text directly
        # or convert this text to a compatible format before analysis.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w+", encoding="utf-8") as temp_resume_file:
            temp_resume_file.write(request.resume_text)
            resume_file_path = temp_resume_file.name

        # Run the ATS analysis flow
        results = ats_analysis_flow(resume_path=resume_file_path, job_description=request.job_description)

        return AtsCheckResponse(
            overall_score=results["overall_score"],
            category_scores=results["category_scores"],
            recommendations=results["recommendations"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up the temporary file
        if resume_file_path and os.path.exists(resume_file_path):
            os.remove(resume_file_path)
