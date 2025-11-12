import os
import sys
import tempfile
import base64
from fastapi import APIRouter, HTTPException
from .models import (
    QuestionGenerateRequest, QuestionGenerateResponse,
    AnalyzeResponseRequest, AnalyzeResponseResponse,
    ReportGenerateRequest, ReportGenerateResponse
)

# Adjust the path to import from the mock_interview package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from mock_interview.audio_processor import AudioProcessor
from mock_interview.interview_analyzer import InterviewAnalyzer
from mock_interview.question_generator import QuestionGenerator
from mock_interview.report_generator import InterviewReportGenerator

router = APIRouter()

# Initialize core components (these can be made dependent if they have state)
audio_processor = AudioProcessor()
interview_analyzer = InterviewAnalyzer()
question_generator = QuestionGenerator()
report_generator = InterviewReportGenerator()

@router.post("/generate-questions", response_model=QuestionGenerateResponse)
async def generate_mock_interview_questions(request: QuestionGenerateRequest):
    try:
        questions = question_generator.generate_questions(
            job_description=request.job_description,
            num_questions=request.num_questions,
            question_types=request.question_types
        )
        return QuestionGenerateResponse(questions=questions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating questions: {str(e)}")

@router.post("/analyze-response", response_model=AnalyzeResponseResponse)
async def analyze_mock_interview_response(request: AnalyzeResponseRequest):
    audio_file_path = None
    try:
        transcript = request.transcript
        audio_features = None

        if request.audio_base64:
            audio_bytes = base64.b64decode(request.audio_base64)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
                temp_audio_file.write(audio_bytes)
                audio_file_path = temp_audio_file.name
            
            # If no transcript provided, generate from audio
            if not transcript:
                transcript = audio_processor.speech_to_text(audio_bytes)
                if transcript == "Could not understand audio":
                    raise ValueError("Could not process audio: speech unrecognisable.")
            
            if request.include_audio_analysis:
                audio_features = audio_processor.analyze_audio_features(audio_bytes)
        
        if not transcript:
            raise ValueError("No transcript or audio provided for analysis.")

        analysis_result = interview_analyzer.analyze_response(
            transcript=transcript,
            question=request.question,
            job_description=request.job_description,
            audio_features=audio_features
        )
        
        feedback = interview_analyzer.generate_feedback(analysis_result)

        return AnalyzeResponseResponse(analysis=analysis_result, feedback=feedback)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing response: {str(e)}")
    finally:
        if audio_file_path and os.path.exists(audio_file_path):
            os.remove(audio_file_path)

@router.post("/generate-report", response_model=ReportGenerateResponse)
async def generate_mock_interview_report(request: ReportGenerateRequest):
    try:
        report_data = report_generator.generate_comprehensive_report(
            interview_session=request.interview_session,
            job_description=request.job_description
        )
        text_report = report_generator.generate_text_report(report_data)
        return ReportGenerateResponse(report_data=report_data, text_report=text_report)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")
