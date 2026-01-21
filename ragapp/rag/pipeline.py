from .retriever import relevant_doc_retriever
from .llm import llm_response

def rag_pipeline(question, top_k, system_prompt):
    content = relevant_doc_retriever(query=question, top_k=top_k)
    if not content:
        yield "No relevant documents found."
        return
    content_str = "\n\n".join(content)
    max_chars = 2000
    if len(content_str) > max_chars:
        content_str = content_str[:max_chars]
    final_answer_list = []
    for chunk in llm_response(
                            system_prompt=system_prompt, 
                            info=content_str,
                            question=question):
        final_answer_list.append(chunk)
        yield chunk