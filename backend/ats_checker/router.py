from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import tempfile
import os

from .models import AtsCheckResponse
from workflows.ats_flow import ats_analysis_flow

router = APIRouter()

@router.post("/check-file", response_model=AtsCheckResponse)
async def check_ats_file(
    resume_file: UploadFile = File(...),
    job_description: str = Form(None)
):
    temp_path = None
    try:
        # Create a temporary file with the same extension
        suffix = os.path.splitext(resume_file.filename)[1] or ".pdf"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            temp_path = tmp.name
            content = await resume_file.read()
            tmp.write(content)

        # Run ATS flow
        results = ats_analysis_flow(
            resume_path=temp_path,
            job_description=job_description
        )

        return AtsCheckResponse(
            overall_score=results["overall_score"],
            category_scores=results["category_scores"],
            recommendations=results["recommendations"]
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
