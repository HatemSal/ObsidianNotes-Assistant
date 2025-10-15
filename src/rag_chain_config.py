from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from src.rag_indexer import prepare_parent_docs, get_retriever
os.environ["GOOGLE_API_KEY"] = "AIzaSyCDtEABJ9JQsbLCg1H8gT_Cj7gYFdVAlUM"


llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

parent_docs = prepare_parent_docs("interviewprep-main")
retriever = get_retriever("chroma_db")
retriever.add_documents(parent_docs)


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: The user's input query (str)
        documents: Retrieved documents (List[Document])
        answer: The final generated answer (str)
    """
    question:str
    documents: Annotated[List[Document], lambda x, y: x + y]
    answer: str

def retrieve(state:GraphState)-> GraphState:
    """
    Retrieves document from vectorstore based on the question.
    """

    print("---Retrieving Documents---")
    question = state['question']
    documents = retriever.invoke(question)

    return {"documents":documents,"question":question}

def generate(state:GraphState)->GraphState:
    print("--- Generating Answer ---")

    question = state['question']
    documents = state['documents']
    prompt = ChatPromptTemplate.from_template(
        """
        You are an expert Q&A assistant that helps students by answering questions using their study notes.
        Use the following context to answer the user's question concisely. 
        If you don't know the answer, just state that you don't know.

        CONTEXT:
        {context}

        QUESTION:
        {question}
        """
    )
    rag_chain = (
        prompt
        | llm
        | StrOutputParser()
    )
    context_text = "\n\n".join(doc.page_content for doc in documents)
    answer = rag_chain.invoke({"question":question, "context":context_text})
    return {"question": question, "documents": documents, "answer": answer}

def prepare_workflow():
    workflow = StateGraph(GraphState)
    workflow.add_node("retrieve",retrieve)
    workflow.add_node("generate",generate)

    workflow.set_entry_point("retrieve")
    workflow.add_edge('retrieve','generate')
    workflow.add_edge('generate',END)

    app = workflow.compile()
    return app

rag_app = prepare_workflow()

def run_rag_chain(question):
    final_state = rag_app.invoke({"question":question})
    return final_state["answer"]
