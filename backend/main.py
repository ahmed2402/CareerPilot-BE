from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from resume_matcher.router import router as resume_matcher_router
from ats_checker.router import router as ats_checker_router
from interview_prep.router import router as interview_prep_router
from mock_interview.router import router as mock_interview_router
from portfolio_api.router import router as portfolio_builder_router

app = FastAPI()

# CORS Middleware
origins = [
    "http://localhost",
    "http://localhost:3000", 
    "http://localhost:8000",
    "http://localhost:5173", 
    "http://localhost:5174" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"]
)

app.mount("/outputs", StaticFiles(directory="./outputs"), name="outputs")

app.include_router(resume_matcher_router, prefix="/resume-matcher", tags=["resume_matcher"])
<<<<<<< HEAD
app.include_router(ats_checker_router, prefix="/ats-checker", tags=["ats_checker"])
app.include_router(interview_prep_router, prefix="/interview-prep", tags=["interview_prep"])
app.include_router(mock_interview_router, prefix="/mock-interview", tags=["mock_interview"])
app.include_router(portfolio_builder_router, prefix="/portfolio-builder", tags=["portfolio_builder"])
=======
# app.include_router(ats_checker_router, prefix="/ats-checker", tags=["ats_checker"])
# app.include_router(interview_prep_router, prefix="/interview-prep", tags=["interview_prep"])
# app.include_router(mock_interview_router, prefix="/mock-interview", tags=["mock_interview"])
>>>>>>> 224233ef2223ff69b8017968abc9359c6753a7bb

@app.get("/ping")
async def ping():
    return {"message": "pong"}


# TODO : UNCOMMENT FOR DEVELOPMENT ( ONLY COMMENT WHEN DEPLOYING )
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)
# Render-ready entry point
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8000))  # Render sets PORT automatically
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port, log_level="info")