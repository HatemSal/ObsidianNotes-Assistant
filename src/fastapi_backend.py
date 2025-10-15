import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from src.rag_chain_config import run_rag_chain
app = FastAPI(title="RAG Agent Backend")

class QueryRequest(BaseModel):
    question:str

@app.post("/rag_query")
async def rag_query_endpoint(request:QueryRequest):
    try:
        rag_answer = run_rag_chain(request.question)
        
        return {
            "question": request.question,
            "answer": rag_answer,
            "status": "success"
        }
    except Exception as e:
        
        print(f"Error during RAG processing: {e}")
        return {
            "question": request.question,
            "answer": f"An internal server error occurred while processing the request: {str(e)}",
            "status": "error"
        }

