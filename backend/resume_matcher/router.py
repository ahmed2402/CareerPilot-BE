from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from .models import ResumeMatchResponse
import os
import shutil
import sys
import time


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from workflows.resume_match_pipeline import app as resume_match_pipeline

router = APIRouter()
@router.post("/match", response_model=ResumeMatchResponse)
async def match_resume(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...)
):
    timestamp = int(time.time() * 1000)
    temp_file_path = f"temp_{timestamp}_{resume_file.filename}"
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(resume_file.file, buffer)

        initial_state = {"resume_path": temp_file_path, "jd_text": job_description}
        final_state = {}
        
        # FIX: Properly extract state from nested stream output
        for output in resume_match_pipeline.stream(initial_state):
            # Each output is like: {"node_name": {actual_state_updates}}
            for node_name, state_updates in output.items():
                if isinstance(state_updates, dict):
                    final_state.update(state_updates)
        
        return ResumeMatchResponse(
            match_score=final_state.get("similarity_score", 0.0),
            insights=final_state.get("insights", {}),
            output_pdf_path=final_state.get("output_pdf_path", "N/A")
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)