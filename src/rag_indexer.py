from langchain_community.document_loaders import ObsidianLoader
import re
from langchain.schema import Document
from langchain_text_splitters import  RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings


def clean_obsidian_links(text):

    text = re.sub(r'^---\s*\n.*?\n---\s*\n', '', text, flags=re.DOTALL | re.MULTILINE)
    text = re.sub(r'\[\[([^\]|]+)\|([^\]]+)\]\]', r'\2', text)
    text = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

    return text

def prepare_parent_docs(obsidian_vault_path):

    loader = ObsidianLoader(obsidian_vault_path, collect_metadata = True)

    documents = loader.load()


    cleaned_documents = []
    for doc in documents:
        cleaned_content = clean_obsidian_links(doc.page_content)
        cleaned_doc = Document(
            page_content = cleaned_content,
            metadata = doc.metadata
        )
        cleaned_documents.append(cleaned_doc)
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap=100)
    
    split_chunks = text_splitter.split_documents(cleaned_documents)
    for chunk in split_chunks:
        source =  chunk.metadata['source'].strip('.md')
        chunk.page_content = source + "\n\n" + chunk.page_content

    
    return split_chunks


def get_vectorstore(vectorstore_dir):

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(
        collection_name="embedded_child_docs",
        embedding_function = embeddings,
        persist_directory = vectorstore_dir
    )
    
    return vectorstore