# Backend API Documentation

This document describes the API endpoints for the ARIA backend, implemented using FastAPI.

## Running the Application

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    (Note: You will need to create a `requirements.txt` file with `fastapi` and `uvicorn`)
3.  Run the FastAPI application using Uvicorn:
    ```bash
    uvicorn main:app --reload
    ```

    The API will be accessible at `http://127.0.0.1:8000`.

## API Endpoints

### General

*   **GET `/ping`**
    *   **Description:** Checks if the API is running.
    *   **Response:**
        ```json
        {
            "message": "pong"
        }
        ```

### Resume Matcher Module

*   **POST `/resume-matcher/match`**
    *   **Description:** Matches a resume against a job description, providing a similarity score, AI-generated insights, and a path to a tailored PDF.
    *   **Request Body (`application/json`):**
        ```json
        {
            "resume_text": "Your resume content here...",
            "job_description": "The job description content here..."
        }
        ```
    *   **Response (`application/json`):**
        ```json
        {
            "match_score": 0.85,
            "insights": {
                "summary": "Your resume aligns well with the job description...",
                "keywords_matched": ["python", "machine learning"],
                "suggestions": "Consider elaborating on project XYZ."
            },
            "output_pdf_path": "/tmp/tailored_resume_123.pdf"
        }
        ```

### ATS Checker Module

*   **POST `/ats-checker/check`**
    *   **Description:** Checks a resume for Applicant Tracking System (ATS) compatibility, providing an overall score, category-specific scores, and actionable recommendations.
    *   **Request Body (`application/json`):**
        ```json
        {
            "resume_text": "Your resume content here...",
            "job_description": "The job description content here..."
        }
        ```
    *   **Response (`application/json`):**
        ```json
        {
            "overall_score": 75.5,
            "category_scores": {
                "format_compatibility": {
                    "score": 0.8,
                    "weight": 0.25,
                    "weighted_score": 0.2
                },
                "keyword_optimization": {
                    "score": 0.7,
                    "weight": 0.25,
                    "weighted_score": 0.175
                }
            },
            "recommendations": [
                "Consider adding more action verbs in your experience section.",
                "Ensure consistent formatting throughout the resume."
            ]
        }
        ```

### Interview Prep Chatbot Module

*   **POST `/interview-prep/prepare`**
    *   **Description:** Engages in a conversational interview preparation, leveraging RAG to answer user questions about technical topics, behavioral scenarios, or interview strategies. It maintains chat history per session.
    *   **Request Body (`application/json`):**
        ```json
        {
            "user_message": "What is a binary tree?",
            "session_id": "user_session_123"
        }
        ```
    *   **Response (`application/json`):**
        ```json
        {
            "ai_response": "A binary tree is a tree data structure in which each node has at most two children, referred to as the left child and the right child..."
        }
        ```

### Mock Interview Analyzer Module

This module provides endpoints for a comprehensive mock interview experience, including question generation, real-time response analysis, and a final performance report.

*   **POST `/mock-interview/generate-questions`**
    *   **Description:** Generates a list of tailored interview questions based on a provided job description and desired question types.
    *   **Request Body (`application/json`):**
        ```json
        {
            "job_description": "Software Engineer at Google...",
            "num_questions": 5,
            "question_types": ["technical", "behavioral"]
        }
        ```
    *   **Response (`application/json`):**
        ```json
        {
            "questions": [
                {
                    "question": "Describe your experience with large-scale distributed systems.",
                    "type": "technical",
                    "difficulty": "hard",
                    "focus_area": "Distributed Systems",
                    "ideal_answer_keywords": ["scalability", "latency", "consistency", "fault tolerance"]
                },
                {
                    "question": "Tell me about a time you had to deal with ambiguity in a project.",
                    "type": "behavioral",
                    "difficulty": "medium",
                    "focus_area": "Adaptability, Problem Solving",
                    "ideal_answer_keywords": ["ambiguity", "clarify", "break down", "iterative approach"]
                }
            ]
        }
        ```

*   **POST `/mock-interview/analyze-response`**
    *   **Description:** Analyzes a candidate's response to an interview question, providing scores across various metrics (clarity, confidence, relevance, etc.) and AI-generated feedback. Supports both text and base64 encoded audio inputs.
    *   **Request Body (`application/json`):**
        ```json
        {
            "transcript": "My experience with distributed systems includes...",
            "audio_base64": "base64_encoded_wav_audio_data_here...",
            "question": "Describe your experience with large-scale distributed systems.",
            "job_description": "Software Engineer, Distributed Systems",
            "include_audio_analysis": true
        }
        ```
    *   **Response (`application/json`):**
        ```json
        {
            "analysis": {
                "overall_score": {
                    "score": 0.78,
                    "details": "Overall: B (78.0%)",
                    "grade": "B",
                    "percentage": 78.0
                },
                "clarity": {
                    "score": 0.85,
                    "details": "Filler words: 2/100 (2.0%)"
                },
                "confidence": {
                    "score": 0.75,
                    "details": "Confidence: 0.75 (volume: 0.8)"
                },
                "fluency": {
                    "score": 0.8,
                    "details": "Fluency: 0.80 (repetition: 0.05%)"
                },
                "relevance": {
                    "score": 0.9,
                    "details": "Relevance: 0.90 (question: 0.9, job: 0.9)"
                },
                "sentiment": {
                    "score": 0.7,
                    "details": "Sentiment: positive (polarity: 0.7)"
                },
                "keyword_match": {
                    "score": 0.88,
                    "details": "Matched 15/17 keywords"
                }
            },
            "feedback": "• Excellent clarity and articulation\n• Good positive attitude\n• Excellent use of relevant keywords"
        }
        ```

*   **POST `/mock-interview/generate-report`**
    *   **Description:** Generates a comprehensive final report for an entire mock interview session, including overall performance, strengths, weaknesses, AI insights, and an improvement plan.
    *   **Request Body (`application/json`):**
        ```json
        {
            "interview_session": {
                "job_description": "Software Engineer at Google...",
                "questions": [...],
                "responses": [...],
                "analyses": [...]
            },
            "job_description": "Software Engineer, Google"
        }
        ```
    *   **Response (`application/json`):**
        ```json
        {
            "report_data": {
                "session_info": {
                    "total_questions": 5,
                    "completed_responses": 5,
                    "session_date": "2023-10-27 10:30:00",
                    "average_response_length": 75.2
                },
                "overall_performance": {
                    "overall_score": 0.78,
                    "grade": "B",
                    "percentage": 78.0,
                    "summary": "Overall performance: B (78.0%)"
                },
                "question_analysis": [
                    {
                        "question_number": 1,
                        "question": "Describe your experience...",
                        "response": "My experience...",
                        "response_length": 50,
                        "scores": {
                            "clarity": 0.8,
                            "confidence": 0.7
                        },
                        "overall_score": 0.75,
                        "grade": "C"
                    }
                ],
                "strengths_weaknesses": {
                    "strengths": ["Strong clarity (85.0%)"],
                    "weaknesses": ["Needs improvement in confidence (55.0%)"],
                    "average_scores": {
                        "clarity": 0.85,
                        "confidence": 0.55
                    }
                },
                "ai_insights": "The candidate demonstrated strong technical knowledge...",
                "recommendations": [
                    "Practice speaking clearly and reduce filler words.",
                    "Work on vocal confidence and body language."
                ],
                "improvement_plan": {
                    "immediate_actions": ["Review STAR method."],
                    "short_term_goals": ["Complete 2 mock interviews."],
                    "long_term_development": ["Develop industry knowledge."],
                    "practice_schedule": {
                        "daily": "15 minutes of question practice",
                        "weekly": "2-3 full mock interviews"
                    }
                }
            },
            "text_report": "MOCK INTERVIEW ANALYSIS REPORT\n..."
        }
        ```

## Postman Collection

To test these endpoints using Postman, you can import the API definitions. A Postman collection will be provided separately, or you can manually create requests based on the above documentation.
