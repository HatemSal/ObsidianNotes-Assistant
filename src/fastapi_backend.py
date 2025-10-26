import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_chain_config import (
    run_rag_chain, 
    process_uploaded_documents, 
    clear_all_documents
)

app = FastAPI(title="RAG Agent Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:3000"],  # Streamlit and React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    mode: str

@app.post("/upload-vault")
async def upload_vault_endpoint(file: UploadFile = File(...)):
    """Upload and process Obsidian vault ZIP file"""
    try:
        
        
        file_content = await file.read()
        
        result = process_uploaded_documents(file_content, file.filename)
        
        if result["success"]:
            return {
                "success": True,
                "message": result["message"],
                "file_count": result["file_count"],
                "documents_added": result["documents_added"],
                "session_id": result["session_id"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error during vault upload: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/rag_query")
async def rag_query_endpoint(request: QueryRequest):
    """Handle RAG queries"""
    try:
        rag_result = run_rag_chain(request.mode,request.query)
        
        return {
            "query": request.query,
            "answer": rag_result["answer"],
            "documents": rag_result["documents"],
            "status": "success"
        }
    except Exception as e:
        print(f"Error during RAG processing: {e}")
        return {
            "question": request.query,
            "answer": f"An internal server error occurred while processing the request: {str(e)}",
            "documents": [],
            "status": "error"
        }



@app.post("/clear-documents")
async def clear_documents_endpoint():
    """Clear all uploaded documents and reset the retriever"""
    try:
        result = clear_all_documents()
        if result["success"]:
            return {
                "success": True,
                "message": result["message"]
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing documents: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

