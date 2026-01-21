import os
from dotenv import load_dotenv
from groq import Groq
load_dotenv()

def llm_response(system_prompt, info, question):
    #Using Groq for LLM
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    # 2. Prepare the messages
    messages = [
        {"role" : "system", "content" : f"{system_prompt}"},
        {"role":"user","content":f"\n\nContext Retrieved :\n{info}\n\nUser Question: {question}"}
    ]
    stream = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_completion_tokens=1024,
        temperature=0.5,
        stream=True,
    )
    for chunk in stream:
        content = chunk.choices[0].delta.content
        if content is not None:
                yield content