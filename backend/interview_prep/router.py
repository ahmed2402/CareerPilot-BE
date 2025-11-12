import os
import sys
from fastapi import APIRouter, HTTPException
from .models import InterviewPrepRequest, InterviewPrepResponse

# Adjust the path to import from rag_core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from rag_core.retriever import get_full_conversational_chain, llm

router = APIRouter()

# Initialize a global chat history store for all sessions. 
# In a production environment, consider a more persistent and scalable solution (e.g., Redis).
chat_history_store = {}

k_retrieval = 5  # Number of documents to retrieve for RAG

# Initialize the conversational chain once when the application starts
try:
    interview_prep_chain = get_full_conversational_chain(llm, k_retrieval, chat_history_store)
except Exception as e:
    print(f"Error initializing conversational chain: {e}")
    # Depending on the error, you might want to exit or provide a fallback
    interview_prep_chain = None

@router.post("/prepare", response_model=InterviewPrepResponse)
async def prepare_interview(request: InterviewPrepRequest):
    if interview_prep_chain is None:
        raise HTTPException(status_code=500, detail="Interview prep service is not initialized.")

    try:
        response = interview_prep_chain.invoke(
            {"input": request.user_message},
            config={"configurable": {"session_id": request.session_id}}
        )
        return InterviewPrepResponse(ai_response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing interview prep request: {str(e)}")
