import os
from dotenv import load_dotenv
from pinecone import Pinecone, SearchQuery

load_dotenv()

def relevant_doc_retriever(query, top_k=3):
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(host=os.getenv("PINECONE_HOST"))

    results = index.search_records(
        namespace="pdf-docs",
        query=SearchQuery(
            inputs = {"text" : query},
            top_k = top_k,
        )
    )

    return [hit['fields']['text'] for hit in results['result']['hits']]