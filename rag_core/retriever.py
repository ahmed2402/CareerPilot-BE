import os
import sys
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers.ensemble import EnsembleRetriever 
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableBranch
from langchain_core.messages import HumanMessage, AIMessage

# Redis history imports (LangChain community)
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain

# Internal project imports
from rag_loader import load_interview_json_files

load_dotenv()

# --- Init LLM ---
groq_api_key = os.environ.get("GROQ_API_KEY", "")
if not groq_api_key:
    raise RuntimeError("Please set GROQ_API_KEY in your environment.")
llm = ChatGroq(groq_api_key=groq_api_key, model_name="llama-3.1-8b-instant")

# --- Redis Config ---
# Allow overriding with env var REDIS_URL
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# --- Configuration Constants ---
KB_DIR = os.path.join(os.path.dirname(__file__), "interview_prep_kb")
VECTORSTORE_PATH = os.path.join(os.path.dirname(__file__), "vectorstores", "interview_prep_faiss")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2" 

# --- Retriever Functions ---
def get_hybrid_retriever(k: int):
    """
    Initializes and returns a hybrid retriever combining FAISS (vector search)
    and BM25 (keyword search) with Reciprocal Rank Fusion (RRF).
    """
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectordb = FAISS.load_local(VECTORSTORE_PATH, embeddings, allow_dangerous_deserialization=True)
    faiss_retriever = vectordb.as_retriever(search_kwargs={"k": k})

    docs = load_interview_json_files(KB_DIR) 
    bm25_retriever = BM25Retriever.from_documents(docs)
    bm25_retriever.k = k

    hybrid_retriever = EnsembleRetriever(
        retrievers=[faiss_retriever, bm25_retriever],
        weights=None,       
        search_type="rrf"   
    )
    return hybrid_retriever

# --- Prompt Definitions ---
SYSTEM_TEMPLATE_RAG = """
You are an expert technical interviewer assistant. Use the following pieces of retrieved context
to answer the question. If you don't know the answer, just say that you don't know.
Do not make up an answer.

Context:
{context}

Question: {input}

Answer:
"""
RAG_PROMPT = ChatPromptTemplate.from_template(SYSTEM_TEMPLATE_RAG)

SYSTEM_TEMPLATE_CONTEXTUALIZE = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood without "
    "the chat history. Do NOT answer the question, just reformulate it "
    "if necessary and otherwise return it as is."
)
CONTEXTUALIZE_Q_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_TEMPLATE_CONTEXTUALIZE),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)

SYSTEM_TEMPLATE_CLASSIFICATION = """Given the following chat history and user question, classify the user's intent as either 'chit_chat' or 'rag_query'. 
Only return 'chit_chat' or 'rag_query'. Do not include any other text.

Chat History: {chat_history}
User Question: {input}"""
CLASSIFICATION_PROMPT = ChatPromptTemplate.from_template(SYSTEM_TEMPLATE_CLASSIFICATION)

SYSTEM_TEMPLATE_CHIT_CHAT = """You are a friendly AI assistant. Engage in a casual conversation with the user.
Keep your responses concise and relevant to the user's input.

Chat History: {chat_history}
User Question: {input}"""
CHIT_CHAT_PROMPT = ChatPromptTemplate.from_template(SYSTEM_TEMPLATE_CHIT_CHAT)

# --- Chain Definitions ---
def get_history_aware_retriever_chain(llm, retriever, k: int):
    """
    Creates a chain that takes chat history and a question, and rewrites the question
    to be standalone if it references past conversation.
    """
    history_aware_retriever = create_history_aware_retriever(
        llm,
        retriever,
        CONTEXTUALIZE_Q_PROMPT
    )
    return history_aware_retriever

def get_rag_chain(llm, k_retrieval: int):
    """
    Combines the history-aware retriever and the document stuffing chain into a
    complete RAG (Retrieval Augmented Generation) workflow.
    """
    hybrid_retriever = get_hybrid_retriever(k_retrieval)
    history_aware_retriever = get_history_aware_retriever_chain(llm, hybrid_retriever, k_retrieval)
    qa_document_chain = create_stuff_documents_chain(llm, RAG_PROMPT)
    
    # The final RAG chain, combining history-aware retrieval with document stuffing
    rag_chain_raw = create_retrieval_chain(history_aware_retriever, qa_document_chain)
    rag_chain = rag_chain_raw | (lambda x: x["answer"])
    return rag_chain

def get_classification_chain(llm):
    """Creates a chain to classify user intent (chit_chat or rag_query)."""
    return CLASSIFICATION_PROMPT | llm | StrOutputParser()

def get_chit_chat_chain(llm):
    """Creates a simple LLM chain for general conversational responses."""
    return CHIT_CHAT_PROMPT | llm | StrOutputParser()

# --- Redis-backed Chat History Helper ---
def get_redis_history(session_id: str) -> RedisChatMessageHistory:
    """
    Return RedisChatMessageHistory for a session id.
    LangChain's RedisChatMessageHistory will persist messages in Redis.
    """
    return RedisChatMessageHistory(session_id=session_id, url=REDIS_URL)

# Utility to convert message history into plain text (for classification prompt)
def messages_to_text(history) -> str:
    """
    Converts various message representations to a single plain-text block:
      - HumanMessage / AIMessage (has .content)
      - dicts with 'type'/'role' and 'content'
      - plain strings
    """
    if not history:
        return ""
    text_lines = []
    for msg in history:
        # LangChain message objects
        if hasattr(msg, "content"):
            role = "User" if isinstance(msg, HumanMessage) else "Assistant"
            text_lines.append(f"{role}: {msg.content}")
        # if msg is a mapping/dict (some message histories store as dict)
        elif isinstance(msg, dict):
            role = msg.get("role") or msg.get("type") or "user"
            content = msg.get("content") or msg.get("text") or ""
            role_name = "User" if role.lower().startswith("human") or role.lower().startswith("user") else "Assistant"
            text_lines.append(f"{role_name}: {content}")
        # fallback: plain string
        else:
            text_lines.append(str(msg))
    return "\n".join(text_lines)

# --- Main Conversational Chain with Routing (Redis-backed) ---
def get_full_conversational_chain(llm, k_retrieval: int):
    """
    Constructs the complete conversational chain, including intent classification
    and routing to either the RAG chain or a chit-chat chain, with Redis-backed history.
    """
    rag_chain_for_branch = get_rag_chain(llm, k_retrieval)
    classification_chain = get_classification_chain(llm)
    chit_chat_chain = get_chit_chat_chain(llm)

    # routing function expects x dict containing 'input' and 'chat_history' (history list)
    def routing_condition(x):
        # Convert injected history to plain text for classifier
        history_text = messages_to_text(x.get("chat_history", []))
        # invoke classification chain with plain text history
        intent_raw = classification_chain.invoke({"input": x["input"], "chat_history": history_text})
        if intent_raw is None:
            intent_raw = ""
        intent = str(intent_raw).strip().lower()
        # Normalize quoted outputs like "'chit_chat'" -> chit_chat
        intent = intent.replace("'", "").replace("\"", "").strip()
        return intent == "chit_chat"

    branch_chain = RunnableBranch(
        (routing_condition, chit_chat_chain),
        rag_chain_for_branch
    )

    # Wrap with RunnableWithMessageHistory to persist history into Redis
    full_chain_with_history = RunnableWithMessageHistory(
        branch_chain,
        lambda session_id: get_redis_history(session_id),
        input_messages_key="input",
        history_messages_key="chat_history",
    )
    return full_chain_with_history

# --- Main Execution for Demonstration ---
if __name__ == "__main__":
    k_retrieval = 5 # Number of documents to retrieve for RAG

    # Build chain (Redis-based history)
    final_conversational_chain = get_full_conversational_chain(llm, k_retrieval)

    print(f"Conversational RAG Chain Initialized (retrieving {k_retrieval} documents).")
    print("Type ':q' to quit.")

    session_id = "user_session_1" # Example session ID for history management

    while True:
        user_input = input("\nYour question: ")
        if user_input.strip().lower() == ':q':
            print("Exiting conversational RAG chain.")
            break

        # RunnableWithMessageHistory expects session_id in config:configurable
        response = final_conversational_chain.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": session_id}}
        )
        print(f"\nAI Interview Prep Assistant: {response}")
