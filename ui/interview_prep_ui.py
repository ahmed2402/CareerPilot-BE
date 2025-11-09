import streamlit as st
import os
import sys
import uuid
from langchain_core.messages import HumanMessage, AIMessage

# Add the parent directory to the sys.path to allow importing rag_core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the main conversational chain and the LLM instance from your RAG core
from rag_core.retriever import get_full_conversational_chain, llm

def show_interview_prep_ui():
    # Set page config
    st.set_page_config(
        page_title="Interview Prep Assistant",
        page_icon="🤖",
        layout="wide",
    )
    
    # --- Global styles (keep your existing CSS here) ---
    st.markdown(
        """
        <style>
            /* Remove Streamlit's default spacing */
            .main .block-container {padding-top: 1rem !important; padding-bottom: 1rem !important;}
            .stApp > div:first-child {padding-top: 1rem !important;}
            
            .app-container {max-width: 800px; margin: 0 auto; padding: 0 1rem;}
            .aria-header h1 {margin-bottom: 0.25rem; text-align: center;}
            .aria-sub {color: #6b7280; margin-top: 0; text-align: center;}
            
            /* Professional chat layout */
            .chat-container {
                max-width: 800px;
                margin: 0.5rem auto 0; /* minimal top margin */
                display: flex;
                flex-direction: column;
                gap: 0.5rem;
            }
            
            /* Chat messages area */
            .chat-messages {
                overflow-y: auto;
                padding: 0.25rem 0; /* minimal padding */
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                background: #fafafa;
                margin-top: 0.25rem; /* minimal top margin */
            }
            
            /* Chat message styling */
            [data-testid="stChatMessage"] {
                font-size: 0.95rem;
                line-height: 1.6;
                margin: 0.5rem 0;
                padding: 0.75rem 1rem;
                border-radius: 12px;
                max-width: 85%;
            }
            
            /* User messages */
            [data-testid="stChatMessage"][data-message-author="user"] {
                background: #3b82f6;
                color: white;
                margin-left: auto;
                margin-right: 0;
            }
            
            /* Assistant messages */
            [data-testid="stChatMessage"][data-message-author="assistant"] {
                background: white;
                color: #1f2937;
                margin-left: 0;
                margin-right: auto;
                border: 1px solid #e5e7eb;
            }
            
            /* Chat input styling */
            .stChatFloatingInputContainer, .stChatInputContainer {
                max-width: 800px;
                margin: 0.25rem auto 0; /* minimal spacing above input */
                position: static; /* avoid extra reserved space from sticky */
                background: transparent;
                padding: 0; /* remove extra padding */
                border-top: none;
            }
            
            /* Input field styling - fix double outline and make fully rounded */
            [data-testid="stChatInput"] textarea, .stTextInput textarea, .stChatInput textarea {
                border: 1px solid #cbd5e1 !important; /* slate-300 */
                border-radius: 9999px !important; /* pill shape */
                padding: 12px 16px !important;
                font-size: 0.95rem !important;
                resize: none !important;
                outline: none !important;
                box-shadow: none !important;
                background: #ffffff !important;
                color: #111827 !important; /* black text for readability */
                caret-color: #111827 !important;
            }
            /* Placeholder color */
            [data-testid="stChatInput"] textarea::placeholder, .stTextInput textarea::placeholder, .stChatInput textarea::placeholder {
                color: #6b7280 !important; /* gray-500 */
                opacity: 1 !important;
            }
            /* Remove wrapper borders/shadows that create double outlines */
            [data-testid="stChatInput"] div, .stTextInput div {
                box-shadow: none !important;
                outline: none !important;
                border: none !important;
                background: transparent !important;
            }
            
            [data-testid="stChatInput"] textarea:focus, .stTextInput textarea:focus, .stChatInput textarea:focus {
                border-color: #3b82f6 !important;
                box-shadow: 0 0 0 2px rgba(59,130,246,0.15) !important;
                outline: none !important;
            }
            
            /* Prompt suggestions */
            .suggestions-container {
                max-width: 800px;
                margin: 0 auto 1rem;
                padding: 0 1rem;
            }
            
            .suggestions-container .stButton > button {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                color: #475569;
                border-radius: 20px;
                padding: 8px 16px;
                font-size: 0.9rem;
                transition: all 0.2s;
            }
            
            .suggestions-container .stButton > button:hover {
                background: #e2e8f0;
                border-color: #cbd5e1;
                transform: translateY(-1px);
            }
            
            /* Divider */
            .soft-divider {
                height: 1px;
                background: linear-gradient(90deg, rgba(0,0,0,0), rgba(0,0,0,0.06), rgba(0,0,0,0));
                margin: 0.5rem 0 0.75rem;
            }
            
            /* Sidebar chat buttons */
            .sidebar-chat {
                padding: 0.5rem;
                border-radius: 0.5rem;
                margin-bottom: 0.5rem;
                cursor: pointer;
            }
            .sidebar-chat:hover {
                background-color: #f0f2f6;
            }
            .sidebar-chat.active {
                background-color: #e6f7ff;
                border-left: 3px solid #1E88E5;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # --- Session State Initialization (MUST be at the top) ---
    if "chat_history_store" not in st.session_state:
        # This holds the LangChain ChatMessageHistory objects for the backend
        st.session_state.chat_history_store = {}

    if "all_chats" not in st.session_state:
        # Initialize with a new chat
        new_chat_id = str(uuid.uuid4())
        st.session_state.all_chats = {
            new_chat_id: {
                "title": "New Chat",
                "messages": []
            }
        }
        
    if "active_chat_id" not in st.session_state and st.session_state.all_chats:
        st.session_state.active_chat_id = next(iter(st.session_state.all_chats))
        
    if "chain" not in st.session_state:
        from rag_core.retriever import llm
        k_retrieval = 5  # Number of documents to retrieve
        st.session_state.chain = get_full_conversational_chain(llm, k_retrieval, st.session_state.chat_history_store)
            

    if "active_chat_id" not in st.session_state or not st.session_state.all_chats:
        # On first run or if no chats exist, create the initial chat
        chat_id = str(uuid.uuid4())
        st.session_state.active_chat_id = chat_id
        st.session_state.all_chats[chat_id] = {
            "title": "New Chat",
            "messages": [{"role": "assistant", "content": "Hello! I'm your AI Interview Prep Assistant. How can I help you today?"}]
        }
    
    # Initialize the RAG chain, passing the central history store from session_state
    if "rag_chain" not in st.session_state:
        st.session_state.rag_chain = get_full_conversational_chain(llm, 5, st.session_state.chat_history_store)

    # --- Sidebar UI ---
    st.sidebar.markdown("### 💬 Interview Prep")
    
    if st.sidebar.button("➕ New Chat", use_container_width=True, type="primary"):
        # Create a new chat and set it as active
        chat_id = str(uuid.uuid4())
        st.session_state.active_chat_id = chat_id
        st.session_state.all_chats[chat_id] = {
            "title": "New Chat",
            "messages": [{"role": "assistant", "content": "I'm ready for our next topic! What's on your mind?"}],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        st.rerun()

    st.sidebar.markdown("---")
    
    # Display chat history buttons in the sidebar with management options
    # Iterate in reverse to show the newest chats first
    for chat_id, chat_data in reversed(list(st.session_state.all_chats.items())):
        col1, col2 = st.sidebar.columns([4, 1])
        
        # Highlight the active chat button
        button_type = "secondary" if chat_id == st.session_state.active_chat_id else "tertiary"
        if col1.button(chat_data['title'], key=f"chat_{chat_id}", use_container_width=True, type=button_type):
            st.session_state.active_chat_id = chat_id
            st.rerun()
        
        # Chat management dropdown
        with col2:
            chat_options = st.empty()
            if chat_options.button("⋮", key=f"options_{chat_id}"):
                st.session_state[f"show_options_{chat_id}"] = not st.session_state.get(f"show_options_{chat_id}", False)
                st.rerun()
            
            if st.session_state.get(f"show_options_{chat_id}", False):
                with st.sidebar.expander("", expanded=True):
                    if st.button("✏️ Rename", key=f"rename_{chat_id}"):
                        st.session_state[f"renaming_{chat_id}"] = True
                        st.rerun()
                    
                    if st.button("🗑️ Delete", key=f"delete_{chat_id}"):
                        if len(st.session_state.all_chats) > 1:  # Ensure at least one chat remains
                            del st.session_state.all_chats[chat_id]
                            # If the active chat was deleted, set a new active chat
                            if st.session_state.active_chat_id == chat_id:
                                st.session_state.active_chat_id = next(iter(st.session_state.all_chats))
                            st.rerun()
        
        # Rename chat interface
        if st.session_state.get(f"renaming_{chat_id}", False):
            with st.sidebar.form(key=f"rename_form_{chat_id}"):
                new_title = st.text_input("New title", value=chat_data["title"])
                col1, col2 = st.columns(2)
                if col1.form_submit_button("Save"):
                    chat_data["title"] = new_title
                    st.session_state[f"renaming_{chat_id}"] = False
                    st.rerun()
                if col2.form_submit_button("Cancel"):
                    st.session_state[f"renaming_{chat_id}"] = False
                    st.rerun()

    # --- Main Chat Interface ---
    # Get the data for the currently active chat
    active_chat = st.session_state.all_chats[st.session_state.active_chat_id]

    st.title("💬 Interview Prep Chatbot")
    st.markdown("<p class='aria-sub'>Ask about data structures, system design, ML, or interview strategy.</p>", unsafe_allow_html=True)
    st.markdown('<div class="soft-divider" style="margin: 0.1rem 0 0.25rem"></div>', unsafe_allow_html=True)

    # Display messages for the currently active chat
    for message in active_chat["messages"]:
        avatar = "🧑‍💻" if message["role"] == "user" else "🤖"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    # --- Chat Input Logic ---
    if prompt := st.chat_input("Ask a question about interview preparation..."):
        # Add user's message to the active chat's list
        active_chat["messages"].append({"role": "user", "content": prompt})

        # If it's the first message in a "New Chat", create a title for it
        if active_chat["title"] == "New Chat":
            # Use the first few words as the chat title
            words = prompt.split()
            title = " ".join(words[:3]) + "..." if len(words) > 3 else prompt
            active_chat["title"] = title
            # Chat history is maintained in session state

        # Display the assistant's response
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("AI is thinking..."):
                try:
                    # Invoke the chain with the correct session_id for history
                    response = st.session_state.chain.invoke(
                        {"input": prompt},
                        config={"configurable": {"session_id": st.session_state.active_chat_id}}
                    )
                    # Handle response based on its type (string or dict)
                    if isinstance(response, dict) and "output" in response:
                        output_text = response["output"]
                    else:
                        # If response is a string or doesn't have "output" key
                        output_text = str(response)
                    
                    st.markdown(output_text)
                    # Add the AI's response to the active chat's list
                    active_chat["messages"].append({"role": "assistant", "content": output_text})
                    
                    # Chat history is maintained in session state
                    
                    # Chat history is maintained in session state
                except Exception as e:
                    error_message = f"I'm sorry, an error occurred: {e}"
                    st.error(error_message)
                    active_chat["messages"].append({"role": "assistant", "content": error_message})
                    # Chat history is maintained in session state
        
        # Rerun to update the UI with the new messages and sidebar title
        st.rerun()

# This allows the file to be run directly as a Streamlit app
if __name__ == "__main__":
    show_interview_prep_ui()