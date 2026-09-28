import hashlib

from google import genai
from google.genai import types

from app.services.config import (
    GEMINI_API_KEY,
    GEMINI_CHAT_MODEL,
    GEMINI_EMBEDDING_MODEL,
)

client = genai.Client(api_key=GEMINI_API_KEY)

FAKE_EMBEDDING_DIM = 16

def embed_texts(texts: list[str]) -> list[list[float]]:
    response = client.models.embed_content(
        model=GEMINI_EMBEDDING_MODEL,
        contents=texts,
    )
    return [item.values for item in response.embeddings]


def generate_answer(question: str, contexts: list) -> str:
    context_text = "\n\n".join(
        [f"Source: {ctx['source']}\n{ctx['text']}" for ctx in contexts]
    )

    response = client.models.generate_content(
        model=GEMINI_CHAT_MODEL,
        contents=f"Based on the following documents, answer the question:\n\nDocuments:\n{context_text}\n\nQuestion: {question}",
        config=types.GenerateContentConfig(
            system_instruction="You are a helpful assistant answering questions based on provided documents.",
        ),
    )

    return response.text
