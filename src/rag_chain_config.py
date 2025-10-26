from typing import TypedDict, Annotated, List
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.agents import AgentExecutor, create_react_agent
import os
import uuid
import zipfile
import tempfile
import shutil
from pathlib import Path
from rag_indexer import prepare_parent_docs, get_vectorstore
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv


load_dotenv()


DOCUMENTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploaded_documents")
CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

vectorstore = get_vectorstore(CHROMA_DB_PATH)

parent_docs = []


# )

QA_PROMPT = ChatPromptTemplate.from_messages([
        ("system","You are an expert Q&A assistant that helps users by answering questions using their obsidian notes. Use the following context to answer the user's question concisely. If you don't know the answer, just state that you don't know.\n\nCONTEXT:\n{context}"),
        ("user","{question}")
    ]
    )



class QAMode :
    """Simple QnA Mode: Retrieve->Generate"""
    def __init__(self):
        self.llm = llm
        self.retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k":6
            }
        )
        self.prompt = QA_PROMPT
        self.output_parser = StrOutputParser()
        self.rag_chain = (
            self.prompt
            | self.llm
            | self.output_parser
        )
    
    def retrieve_docs(self,question):
        query_enhancer = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")
        enhancement_prompt = ChatPromptTemplate.from_messages([
            ("system","You are an expert assistant that helps users extract information from their notes"),
            ("system","Based on a user's question, you will generate three queries to extract information from the notes that will help answer the question"),
            ("system","You must generate queries that are diverse from each other but at the same time each of them is specific to a topic that will help answer the question"),
            ("system", "Your output must be a valid JSON Object. The keys are 'query1', 'query2' and 'query3' and the values are the generated queries"),
            ("system","Output ONLY The JSON Object with no additional comments"),
            ("system", "Example output:\n {{'query1':'Binary search trees structure', 'query2':'Hashmaps structure', 'query3':'Linked list structure'}}"),
            ("user","{question}")
        ])
        
        
        
        enhancement_chain = enhancement_prompt | query_enhancer | JsonOutputParser()
        result = enhancement_chain.invoke({"question":question})
        print(result)
        docs = []
        seen_contents = set()
        for k, v in result.items():
            query_docs = self.retriever.invoke(v)
            for d in query_docs:
                content = d.page_content.strip()
                if content not in seen_contents:
                    docs.append(d)
                    seen_contents.add(content)

        return docs
            
        
        
    def run(self, question:str):
        documents = self.retrieve_docs(question)
        context_text = "\n\n".join(doc.page_content for doc in documents)
        answer = self.rag_chain.invoke({"question":question, "context":context_text})
        return {"query": question, "documents": documents, "answer": answer}

class SummarizeMode:
    def __init__(self):
        
        self.retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k":5,
                "lambda_mult":0.5
            }
        )
        self.llm = llm
        self.retrieved_docs = []
        self.seen_doc_ids = set()  
        
        @tool
        def search_vault(query:str)->str:
            """Search the Obsidian vault for information. Use this to gather context before summarizing"""
            docs = self.retriever.invoke(query)
            
            for doc in docs:
                doc_id = doc.metadata.get('source', 'unknown')
                if doc_id not in self.seen_doc_ids:
                    self.seen_doc_ids.add(doc_id)
                    self.retrieved_docs.append(doc)
            
            results = []
            for i, doc in enumerate(docs, 1):
                source = doc.metadata.get('source', 'Unknown')
                results.append(f"[{i}] Source: {source}\n{doc.page_content}\n")
            
            return "\n".join(results)
        
        self.search_tool = search_vault
        
        template = """You are a summarization expert with access to an Obsidian knowledge base.
        Your task is to create a comprehensive summary of the given topic using the knowledge base.

        You have access to the following tools:

        {tools}

        Use the following format:

        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: the final answer to the original input question

        Begin!

        Question: Create a comprehensive summary about: {input}
        Thought:{agent_scratchpad}"""
        prompt = PromptTemplate.from_template(template)
        
        self.agent = create_react_agent(
            self.llm,
            [self.search_tool],
            prompt
        )
        self.agent_executor = AgentExecutor(
            agent=self.agent, 
            tools=[self.search_tool], 
            handle_parsing_errors=True,
            max_iterations=20,
            max_execution_time=300,
            verbose=True
        )
        
    def run(self, topic:str):
        self.retrieved_docs = []
        self.seen_doc_ids = set()
        result = self.agent_executor.invoke({"input":topic})
        return {"query": topic, "documents": self.retrieved_docs, "answer": result["output"]}


class ObsidianAgent:
    def __init__(self):
        self.qa_mode = QAMode()
        self.summarize_mode = SummarizeMode()
    
    def run(self, mode, input_text):
        mode = mode.lower()
        
        if mode == "qa":
            return self.qa_mode.run(input_text)
        elif mode == "summarize":
            return self.summarize_mode.run(input_text)

agent = ObsidianAgent()

def run_rag_chain(mode,input_text):
    final_state = agent.run(mode, input_text)
    
    documents = final_state.get("documents", [])
    documents_unique =[]
    for doc in documents:
        if doc.metadata.get("source","unknown") not in documents_unique:
            documents_unique.append(doc)
    document_info = []
    
    for doc in documents_unique:
        doc_info = {
            "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
            "metadata": doc.metadata
        }
        title = doc.metadata.get("source", "Unknown Document")
        if isinstance(title, str) and "/" in title:
            title = title.split("/")[-1]  
        if title.endswith(".md"):
            title = title[:-3]  
        
        doc_info["title"] = title
        document_info.append(doc_info)
    
    return {
        "answer": final_state["answer"],
        "documents": document_info
    }






def process_uploaded_documents(file_content: bytes, filename: str) -> dict:
  
    try:
        
        documents_path = Path(DOCUMENTS_DIR)
        documents_path.mkdir(exist_ok=True)
        
      
        session_id = str(uuid.uuid4())
        session_dir = documents_path / session_id
        session_dir.mkdir(exist_ok=True)
        
        
        temp_file_path = session_dir / filename
        with open(temp_file_path, "wb") as buffer:
            buffer.write(file_content)
        
        
        with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
            zip_ref.extractall(session_dir)
        
        
        markdown_files = list(session_dir.rglob("*.md"))
        
        
        
        try:
            new_docs = prepare_parent_docs(str(session_dir))
            
            
            vectorstore.add_documents(new_docs)
        
            global parent_docs
            parent_docs.extend(new_docs)
            
    
            os.unlink(temp_file_path)
            
            return {
                "success": True,
                "message": f"Successfully processed {len(new_docs)} documents",
                "file_count": len(markdown_files),
                "session_id": session_id,
                "documents_added": len(new_docs)
            }
            
        except Exception as processing_error:
            
            shutil.rmtree(session_dir)
            print(processing_error)
            return {
                "success": False,
                "error": f"Error processing documents: {str(processing_error)}",
                "file_count": len(markdown_files)
            }
            
    except Exception as e:
        print(e)
        return {
            "success": False,
            "error": f"Error during document processing: {str(e)}",
            "file_count": 0
        }


def clear_all_documents() -> dict:
    """
    Clear all uploaded documents and reset the retriever.
    
    Returns:
        dict: Result of the clearing operation
    """
    try:
        global parent_docs
        
        
        documents_path = Path(DOCUMENTS_DIR)
        if documents_path.exists():
            shutil.rmtree(documents_path)
        
        documents_path.mkdir(exist_ok=True)
        
        
        parent_docs = []
        
        global vectorstore
        vectorstore = get_vectorstore(CHROMA_DB_PATH)
        
        return {
            "success": True,
            "message": "All documents cleared successfully",
            "documents_cleared": True
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error clearing documents: {str(e)}"
        }


