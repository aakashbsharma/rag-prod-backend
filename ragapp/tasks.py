import os
import hashlib
from dotenv import load_dotenv
from celery import shared_task
from pinecone import Pinecone
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

@shared_task
def process_and_store_pinecone(file_path):
    # 1. Standard Loading & Chunking
    loader = PyMuPDFLoader(file_path)
    pages = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = text_splitter.split_documents(pages)

    # 2. Connect to Pinecone
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(host=os.getenv("PINECONE_HOST"))

    # 3. Format records with Deterministic IDs
    records = []
    for i, chunk in enumerate(chunks):
        # Create unique ID based on content + filename
        content = chunk.page_content
        unique_id = hashlib.sha256(f"{file_path}{content}".encode()).hexdigest()
        
        records.append({
            "_id": unique_id,
            "text": content, # This key must match your index 'field_map'
        })

    # 4. Upsert (Pinecone does the embedding work!)
    index.upsert_records(namespace="pdf-docs", records=records)

    return {"status": "completed", "chunks": len(records)}