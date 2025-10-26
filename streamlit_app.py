import streamlit as st
import requests
import json
from typing import List, Dict

# Configuration
BACKEND_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Notes RAG Agent",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for ChatGPT-like interface with white/green theme
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background-color: #ffffff;
    }
    
    /* Header Styles */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #ffffff 0%, #f8fff8 100%);
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(76, 175, 80, 0.1);
    }
    
    .main-title {
        color: #2e7d32;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .main-subtitle {
        color: #4caf50;
        font-size: 1.1rem;
        font-weight: 400;
    }
    
    /* Upload Section */
    .upload-section {
        background: linear-gradient(135deg, #ffffff 0%, #f1f8e9 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid #e8f5e9;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.1);
    }
    
    /* Chat Interface */
    .chat-header {
        background: linear-gradient(90deg, #4caf50 0%, #66bb6a 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 15px 15px 0 0;
        margin-bottom: 0;
        font-weight: 600;
        font-size: 1.2rem;
    }
    
    .chat-container {
        background-color: #ffffff;
        border: 1px solid #e8f5e9;
        border-radius: 15px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 10px rgba(76, 175, 80, 0.05);
        overflow: hidden;
    }
    
    .user-message {
        background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
        padding: 1rem 1.5rem;
        border-left: 4px solid #4caf50;
        margin: 0.5rem 0;
        border-radius: 10px;
    }
    
    .assistant-message {
        background-color: #ffffff;
        padding: 1rem 1.5rem;
        border-left: 4px solid #81c784;
        margin: 0.5rem 0;
        border-radius: 10px;
        border: 1px solid #f1f8e9;
    }
    
    .message-label {
        font-weight: 600;
        color: #2e7d32;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .mode-indicator {
        background-color: #4caf50;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    /* Mode Selection Dropdown */
    .mode-selector {
        background: linear-gradient(135deg, #ffffff 0%, #f8fff8 100%);
        border: 2px solid #4caf50;
        border-radius: 12px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(76, 175, 80, 0.1);
    }
    
    .mode-dropdown {
        background-color: #ffffff;
        border: 2px solid #4caf50;
        border-radius: 8px;
        color: #2e7d32;
        font-weight: 500;
        padding: 0.5rem 1rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .mode-dropdown:hover {
        background-color: #f1f8e9;
        border-color: #2e7d32;
    }
    
    .mode-dropdown:focus {
        outline: none;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2);
    }
    
    /* Input Area */
    .input-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8fff8 100%);
        border: 2px solid #e8f5e9;
        border-radius: 15px;
        padding: 1.5rem;
        margin-top: 1rem;
        box-shadow: 0 2px 10px rgba(76, 175, 80, 0.05);
    }
    
    .stTextInput > div > div > input {
        border: 2px solid #4caf50;
        border-radius: 25px;
        padding: 0.8rem 1.2rem;
        font-size: 1rem;
        background-color: #ffffff;
        color: #2e7d32;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2e7d32;
        box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.2);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #4caf50 0%, #66bb6a 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #2e7d32 0%, #4caf50 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Secondary Buttons */
    .secondary-button {
        background: linear-gradient(135deg, #ffffff 0%, #f1f8e9 100%);
        color: #4caf50;
        border: 2px solid #4caf50;
        border-radius: 25px;
        padding: 0.6rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .secondary-button:hover {
        background: linear-gradient(135deg, #4caf50 0%, #66bb6a 100%);
        color: white;
    }
    
    /* Document Cards */
    .document-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fff8 100%);
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 4px solid #4caf50;
        margin-bottom: 0.8rem;
        box-shadow: 0 2px 8px rgba(76, 175, 80, 0.1);
        transition: all 0.3s ease;
    }
    
    .document-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.15);
    }
    
    .document-title {
        font-weight: 600;
        color: #2e7d32;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }
    
    .document-content {
        font-size: 0.9rem;
        color: #4caf50;
        font-style: italic;
        line-height: 1.4;
    }
    
    /* Sidebar */
    .sidebar-header {
        background: linear-gradient(135deg, #4caf50 0%, #66bb6a 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        text-align: center;
        font-weight: 600;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f8e9;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #4caf50;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #2e7d32;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'documents_uploaded' not in st.session_state:
        st.session_state.documents_uploaded = False
    if 'last_retrieved_docs' not in st.session_state:
        st.session_state.last_retrieved_docs = []
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'upload'
    if 'selected_mode' not in st.session_state:
        st.session_state.selected_mode = 'qa'

def upload_vault(uploaded_file):
    """Upload Obsidian vault to backend"""
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/zip")}
        response = requests.post(f"{BACKEND_URL}/upload-vault", files=files)
        
        if response.status_code == 200:
            result = response.json()
            return True, result
        else:
            error_detail = response.json().get("detail", "Unknown error")
            return False, {"error": error_detail}
    except requests.exceptions.ConnectionError:
        return False, {"error": "Cannot connect to backend. Make sure the FastAPI server is running on port 8000."}
    except Exception as e:
        return False, {"error": str(e)}

def query_rag(query: str, mode: str):
    """Send query to RAG backend"""
    try:
        payload = {"query": query, "mode": mode}
        response = requests.post(f"{BACKEND_URL}/rag_query", json=payload)
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {"error": "Failed to get response from backend"}
    except requests.exceptions.ConnectionError:
        return False, {"error": "Cannot connect to backend. Make sure the FastAPI server is running on port 8000."}
    except Exception as e:
        return False, {"error": str(e)}

def clear_documents():
    """Clear all documents from backend"""
    try:
        response = requests.post(f"{BACKEND_URL}/clear-documents")
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, {"error": "Failed to clear documents"}
    except requests.exceptions.ConnectionError:
        return False, {"error": "Cannot connect to backend"}
    except Exception as e:
        return False, {"error": str(e)}



def upload_page():
    """Upload page for vault upload"""
    st.markdown('''
    <div class="main-header fade-in">
        <h1 class="main-title">📚 Notes RAG Agent</h1>
        <p class="main-subtitle">Transform your Obsidian vault into an intelligent knowledge assistant</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Center the upload section
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="upload-section fade-in">', unsafe_allow_html=True)
        st.markdown('<h3 style="color: #2e7d32; text-align: center; margin-bottom: 1.5rem;">📁 Upload Your Obsidian Vault</h3>', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose your Obsidian vault ZIP file",
            type=['zip'],
            help="Upload a ZIP file containing your Obsidian vault",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            st.markdown(f'''
            <div style="background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%); 
                        padding: 1rem; border-radius: 10px; margin: 1rem 0; 
                        border-left: 4px solid #4caf50;">
                <strong style="color: #2e7d32;">📄 Selected file:</strong> 
                <span style="color: #4caf50;">{uploaded_file.name}</span>
            </div>
            ''', unsafe_allow_html=True)
            
            if st.button("🚀 Upload & Process Vault", type="primary", use_container_width=True):
                with st.spinner("🔄 Processing your vault..."):
                    success, result = upload_vault(uploaded_file)
                    
                    if success:
                        st.session_state.documents_uploaded = True
                        st.session_state.current_page = 'chat'
                        st.success(f"✅ {result['message']}")
                        st.info(f"📄 Files processed: {result['file_count']}")
                        st.info(f"📚 Documents added: {result['documents_added']}")
                        st.balloons()
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.error(f"❌ Upload failed: {result['error']}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Instructions with better styling
        st.markdown('''
        <div style="margin-top: 2rem; padding: 1.5rem; background: linear-gradient(135deg, #ffffff 0%, #f8fff8 100%); 
                    border-radius: 12px; border: 1px solid #e8f5e9;">
            <h4 style="color: #2e7d32; margin-bottom: 1rem;">💡 How to Prepare Your Vault</h4>
            <div style="color: #4caf50; line-height: 1.6;">
                <p><strong>1.</strong> Export your Obsidian vault as a ZIP file</p>
                <p><strong>2.</strong> Ensure it contains <code>.md</code> files</p>
                <p><strong>3.</strong> Upload the ZIP file using the button above</p>
                <p><strong>4.</strong> Wait for processing to complete</p>
                <p><strong>5.</strong> Start chatting with your notes!</p>
            </div>
        </div>
        ''', unsafe_allow_html=True)

def chat_page():
    """ChatGPT-like chat page for conversational interface"""
    # Header with navigation
    col_header, col_nav = st.columns([4, 1])
    
    with col_header:
        st.markdown('''
        <div class="chat-header fade-in">
            💬 Chat with Your Notes
        </div>
        ''', unsafe_allow_html=True)
    
    with col_nav:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🔄 New Vault", help="Upload a new vault"):
            success, result = clear_documents()
            if success:
                st.session_state.documents_uploaded = False
                st.session_state.chat_history = []
                st.session_state.last_retrieved_docs = []
                st.session_state.current_page = 'upload'
                st.rerun()
    
    # Create two columns: main chat and sidebar
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Elegant Mode Selection Dropdown
        st.markdown('<div class="mode-selector">', unsafe_allow_html=True)
        st.markdown('<h4 style="color: #2e7d32; margin-bottom: 0.8rem;">🎯 Select AI Mode</h4>', unsafe_allow_html=True)
        
        mode_options = {
            'qa': '❓ Q&A Mode - Ask specific questions',
            'summarize': '📝 Summarize Mode - Get comprehensive summaries'
        }
        
        selected_mode_display = st.selectbox(
            "Choose how you want to interact with your notes:",
            options=list(mode_options.keys()),
            format_func=lambda x: mode_options[x],
            index=0 if st.session_state.selected_mode == 'qa' else 1,
            key="mode_selector"
        )
        
        if selected_mode_display != st.session_state.selected_mode:
            st.session_state.selected_mode = selected_mode_display
            st.rerun()
        
        # Mode description
        if st.session_state.selected_mode == 'qa':
            st.markdown('''
            <div style="background: linear-gradient(135deg, #e3f2fd 0%, #e8f5e9 100%); 
                        padding: 0.8rem; border-radius: 8px; margin-top: 0.5rem;">
                <span style="color: #2e7d32;">💡 <strong>Q&A Mode:</strong> Ask specific questions about your notes and get direct, focused answers.</span>
            </div>
            ''', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div style="background: linear-gradient(135deg, #fff3e0 0%, #e8f5e9 100%); 
                        padding: 0.8rem; border-radius: 8px; margin-top: 0.5rem;">
                <span style="color: #2e7d32;">💡 <strong>Summarize Mode:</strong> Request comprehensive summaries on topics from your notes.</span>
            </div>
            ''', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat History with ChatGPT-like styling
        if st.session_state.chat_history:
            st.markdown('<div style="margin: 1.5rem 0;">', unsafe_allow_html=True)
            for i, chat_item in enumerate(st.session_state.chat_history):
                # Handle both old format (3 items) and new format (4 items)
                if len(chat_item) == 4:
                    query, answer, docs, mode = chat_item
                else:
                    query, answer, docs = chat_item
                    mode = 'qa'  # Default to qa for old entries
                
                # User message
                mode_emoji = "❓" if mode == 'qa' else "📝"
                st.markdown(f'''
                <div class="user-message fade-in">
                    <div class="message-label">
                        🧑‍💻 You 
                        <span class="mode-indicator">{mode_emoji} {mode.upper()}</span>
                    </div>
                    <div>{query}</div>
                </div>
                ''', unsafe_allow_html=True)
                
                # Assistant message
                st.markdown(f'''
                <div class="assistant-message fade-in">
                    <div class="message-label">🤖 Assistant</div>
                    <div>{answer}</div>
                </div>
                ''', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Input area with ChatGPT-like styling
        st.markdown('<div class="input-container">', unsafe_allow_html=True)
        
        if st.session_state.selected_mode == 'qa':
            user_input = st.text_input(
                "",
                placeholder="💭 Ask a question about your notes...",
                key="qa_input",
                label_visibility="collapsed"
            )
        else:
            user_input = st.text_input(
                "",
                placeholder="📝 What topic would you like me to summarize?",
                key="summarize_input",
                label_visibility="collapsed"
            )
        
        # Send button with better styling
        col_send, col_clear = st.columns([3, 1])
        with col_send:
            send_button = st.button("🚀 Send Message", type="primary", disabled=not user_input, use_container_width=True)
        with col_clear:
            clear_button = st.button("🗑️ Clear", use_container_width=True)
        
        if clear_button:
            st.session_state.chat_history = []
            st.session_state.last_retrieved_docs = []
            st.rerun()
        
        if send_button and user_input:
            with st.spinner(f"🤔 {'Thinking about your question' if st.session_state.selected_mode == 'qa' else 'Creating comprehensive summary'}..."):
                success, result = query_rag(user_input, st.session_state.selected_mode)
                
                if success:
                    answer = result['answer']
                    documents = result.get('documents', [])
                    
                    # Add to chat history with mode
                    st.session_state.chat_history.append((user_input, answer, documents, st.session_state.selected_mode))
                    st.session_state.last_retrieved_docs = documents
                    
                    # Clear input and rerun
                    st.rerun()
                else:
                    st.error(f"❌ Query failed: {result['error']}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Elegant sidebar for retrieved documents
        st.markdown('<div class="sidebar-header">📄 Source Documents</div>', unsafe_allow_html=True)
        
        if st.session_state.last_retrieved_docs:

            
            # Remove duplicates based on title and source
            seen_docs = set()
            unique_docs = []
            
            for doc in st.session_state.last_retrieved_docs:
                title = doc.get('title', 'Unknown Document')
                source = doc.get('metadata', {}).get('source', 'Unknown Source')
                doc_key = f"{title}_{source}"
                
                if doc_key not in seen_docs:
                    seen_docs.add(doc_key)
                    unique_docs.append(doc)
            

            
            for i, doc in enumerate(unique_docs):
                # Document title only
                title = doc.get('title', f'Document {i+1}')
                st.markdown(f'<div style="color: #2e7d32; font-weight: 600; margin-bottom: 0.2rem;">📄 {title}</div>', unsafe_allow_html=True)
                
                # Source information only
                metadata = doc.get('metadata', {})
                if metadata.get('source'):
                    source = metadata['source']
                    if isinstance(source, str) and '/' in source:
                        source = source.split('/')[-1]
                    st.markdown(f'<div style="color: #81c784; font-size: 0.9rem; margin-bottom: 1rem; font-weight: 500;">📁 {source}</div>', unsafe_allow_html=True)
        else:
            st.markdown('''
            <div style="background: linear-gradient(135deg, #f5f5f5 0%, #f8fff8 100%); 
                        padding: 1.5rem; border-radius: 12px; text-align: center; 
                        border: 2px dashed #4caf50; color: #4caf50;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📝</div>
                <div><strong>Send a message</strong></div>
                <div style="font-size: 0.9rem; margin-top: 0.3rem;">to see relevant documents here</div>
            </div>
            ''', unsafe_allow_html=True)

def main():
    initialize_session_state()
    
    # Route to appropriate page
    if not st.session_state.documents_uploaded or st.session_state.current_page == 'upload':
        upload_page()
    else:
        chat_page()

if __name__ == "__main__":
    import time
    main()