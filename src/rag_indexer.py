from langchain_community.document_loaders import ObsidianLoader
import re
from langchain.schema import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain.storage import InMemoryStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.retrievers import ParentDocumentRetriever

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

    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ('###',"Header 3")
    ]

    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on = headers_to_split_on)

    parent_docs =[]
    for doc in cleaned_documents:
        splits = markdown_splitter.split_text(doc.page_content)
        for split in splits:
            split.metadata.update(doc.metadata)
        parent_docs.extend(splits)
    
    return parent_docs


def get_retriever(vectorstore_dir):

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(
        collection_name="embedded_child_docs",
        embedding_function = embeddings,
        persist_directory = vectorstore_dir
    )
   
    docstore = InMemoryStore()

    character_splitter = RecursiveCharacterTextSplitter(chunk_size = 1000, chunk_overlap=100)

    retriever = ParentDocumentRetriever(
        vectorstore = vectorstore,
        docstore = docstore,
        child_splitter = character_splitter,
    )
    
    return retriever