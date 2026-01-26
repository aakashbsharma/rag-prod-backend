import os
import hashlib
from dotenv import load_dotenv
from celery import shared_task
from pinecone import Pinecone
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from unstructured_client import UnstructuredClient
from unstructured_client.models import operations, shared

load_dotenv()

@shared_task
def process_with_unstructured_limited(file_path):
    client = UnstructuredClient(api_key_auth=os.getenv("UNSTRUCTURED_API_KEY"))
    # 1. Get the actual page count
    reader = PdfReader(file_path)
    total_pages = len(reader.pages)
    
    # 2. Set the end of the range to 10 or the total, whichever is smaller
    end_page = min(10, total_pages)

    with open(file_path, "rb") as f:
        data = f.read()

    req = operations.PartitionRequest(
        partition_parameters=shared.PartitionParameters(
            files=shared.Files(content=data, file_name=file_path),
            strategy=shared.Strategy.HI_RES,
            # This is the key: only process pages 1 through 10
            split_pdf_page_range=[1, end_page], 
            split_pdf_page=True # Required for the range parameter to work
        )
    )

    try:
        res = client.general.partition(request=req)
        # Combine the elements into text
        full_text = "\n\n".join([el['text'] for el in res.elements])
        del res
        import gc
        gc.collect()
    except Exception as e:
        print(f"API Error: {e}")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = text_splitter.split_text(full_text)
    # 2. Connect to Pinecone
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(host=os.getenv("PINECONE_HOST"))
    try:
        dictionary = index.delete(delete_all=True, namespace="pdf-docs")
    except Exception as e :
        pass
    # 3. Format records with Deterministic IDs
    records = []
    for i, chunk_content in enumerate(chunks):
        unique_id = hashlib.sha256(f"{file_path}{chunk_content}".encode()).hexdigest()
        records.append({
            "_id": unique_id,
            "text": chunk_content,  # Integrated Inference uses this field
        })

    # 4. Upsert (Pinecone does the embedding work!)
    index.upsert_records(namespace="pdf-docs", records=records)

    return {"status": "completed", "chunks": len(records)}