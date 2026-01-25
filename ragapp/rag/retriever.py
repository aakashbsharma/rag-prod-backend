import os
from dotenv import load_dotenv
from pinecone import Pinecone, SearchQuery

load_dotenv()

def relevant_doc_retriever(query, rank=2, top_k=5):
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(host=os.getenv("PINECONE_HOST"))

    results = index.search_records(
        namespace="pdf-docs",
        query=SearchQuery(
            inputs = {"text" : query},
            top_k = top_k,
        ),
        rerank={
        "model": "bge-reranker-v2-m3",
        "top_n": rank,
        "rank_fields": ["text"]
        }
    )

    return [hit['fields']['text'] for hit in results['result']['hits']]