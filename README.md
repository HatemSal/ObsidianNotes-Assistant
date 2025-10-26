# 🧠 RAG Agent - Obsidian Knowledge Assistant

A sophisticated RAG (Retrieval-Augmented Generation) system that transforms your Obsidian vault into an intelligent, conversational knowledge assistant. Upload your notes and chat with your personal knowledge base using AI.

## ✨ Features

- **🎨 ChatGPT-like Interface**: Modern Streamlit web app with elegant white/green design
- **📁 Obsidian Integration**: Upload your Obsidian vault as a ZIP file for instant processing
- **🤖 Dual AI Modes**: 
  - **Q&A Mode**: Ask specific questions and get direct answers
  - **Summarize Mode**: Request comprehensive summaries on any topic
- **🔍 Smart Retrieval**: Advanced document retrieval with source attribution
- **⚡ Real-time Processing**: Automatic document indexing and embedding generation
- **📱 Responsive Design**: Clean, modern interface that works on all devices

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Google AI API Key (for Gemini)

### Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/notes-rag-agent.git
   cd notes-rag-agent
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv ragagent
   
   # Windows
   ragagent\Scripts\activate
   
   # macOS/Linux
   source ragagent/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API key**:
   - Get your Google AI API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a `.env` file in the project root:
     ```env
     GOOGLE_API_KEY=your_google_api_key_here
     ```

5. **Start the application**:
   
   **Option A: Automated (Recommended)**
   ```bash
   # Windows
   start_streamlit.bat
   
   # Cross-platform
   python start_streamlit.py
   ```
   
   **Option B: Manual**
   ```bash
   # Terminal 1: Start Backend
   cd src
   python fastapi_backend.py
   
   # Terminal 2: Start Frontend
   streamlit run streamlit_app.py
   ```

6. **Open your browser** and navigate to `http://localhost:8501`

## 📱 How to Use

### 1. Upload Your Obsidian Vault
- Export your Obsidian vault as a ZIP file
- Use the elegant upload interface to select your file
- Wait for automatic processing and indexing

### 2. Select AI Mode
- **Q&A Mode**: Perfect for specific questions about your notes
- **Summarize Mode**: Great for comprehensive topic overviews

### 3. Start Chatting
- Ask questions in natural language
- View source documents in the sidebar
- Switch between modes anytime during conversation

### 4. Explore Your Knowledge
- Get instant answers from your personal knowledge base
- See which documents contributed to each response
- Build on previous conversations seamlessly

## 🏗️ Architecture

### Backend (FastAPI + LangChain)
- **🔧 FastAPI Server**: RESTful API with automatic documentation
- **📄 Document Processing**: Markdown parsing with Obsidian link cleaning
- **🧠 LangChain Integration**: Advanced RAG pipeline with LangGraph
- **🔍 Vector Search**: ChromaDB for semantic similarity search
- **🤖 AI Models**: Google Gemini for generation, HuggingFace for embeddings

### Frontend (Streamlit)
- **🎨 Modern UI**: ChatGPT-inspired interface with custom CSS
- **📱 Responsive Design**: Clean white/green theme
- **🔄 Real-time Updates**: Instant chat responses and document display
- **📊 State Management**: Session-based conversation history

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root:
```env
GOOGLE_API_KEY=your_google_api_key_here
```

### API Endpoints
- `POST /upload-vault` - Upload and process Obsidian vault ZIP file
- `POST /rag_query` - Send queries with mode selection (qa/summarize)
- `POST /clear-documents` - Clear all uploaded documents

### Customization
- **Embedding Model**: Change in `src/rag_indexer.py` (default: all-MiniLM-L6-v2)
- **LLM Model**: Modify in `src/rag_chain_config.py` (default: gemini-2.5-flash)
- **Chunk Sizes**: Adjust in `src/rag_indexer.py` for different document sizes
- **UI Theme**: Customize colors in `streamlit_app.py` CSS section

## 📁 Project Structure

```
notes-rag-agent/
├── src/                      # Backend source code
│   ├── fastapi_backend.py    # FastAPI application & API endpoints
│   ├── rag_chain_config.py   # RAG pipeline & AI modes
│   └── rag_indexer.py        # Document processing & embeddings
├── streamlit_app.py          # Streamlit frontend application
├── start_streamlit.bat       # Windows startup script
├── start_streamlit.py        # Cross-platform startup script
├── requirements.txt          # Python dependencies
├── uploaded_documents/       # Processed vault storage (auto-created)
├── chroma_db/               # Vector database storage (auto-created)
└── README.md                # Project documentation
```

## 🎯 Use Cases

- **📚 Research**: Query your research notes and papers
- **📝 Study Aid**: Get summaries of complex topics from your notes
- **💡 Knowledge Discovery**: Find connections between different concepts
- **📖 Personal Wiki**: Turn your Obsidian vault into a searchable knowledge base
- **🎓 Academic Work**: Quickly reference and cite your note sources

## 🛠️ Development

### Tech Stack
- **Backend**: FastAPI, LangChain, ChromaDB, Google Gemini
- **Frontend**: Streamlit with custom CSS
- **Embeddings**: HuggingFace Sentence Transformers
- **Vector DB**: ChromaDB with persistent storage

**Transform your notes into an intelligent knowledge companion! 🧠✨**
