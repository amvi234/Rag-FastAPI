import hashlib

from openai import OpenAI

from app.services.config import (
    LLM_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_CHAT_MODEL,
    OPENAI_EMBEDDING_MODEL,
)

client = OpenAI(api_key=OPENAI_API_KEY) if LLM_PROVIDER != "fake" else None

FAKE_EMBEDDING_DIM = 16


def _fake_embedding(text: str) -> list[float]:
    """Deterministic pseudo-embedding: same text always maps to the same
    vector, and the vector size matches real usage, so ingest + search
    stay consistent while testing without a real model."""
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return [byte / 255 for byte in digest[:FAKE_EMBEDDING_DIM]]


def embed_texts(texts: list[str]) -> list[list[float]]:
    if LLM_PROVIDER == "fake":
        return [_fake_embedding(text) for text in texts]

    response = client.embeddings.create(
        model=OPENAI_EMBEDDING_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]


def generate_answer(question: str, contexts: list) -> str:
    context_text = "\n\n".join(
        [f"Source: {ctx['source']}\n{ctx['text']}" for ctx in contexts]
    )

    if LLM_PROVIDER == "fake":
        sources = ", ".join(ctx["source"] for ctx in contexts) or "no matching sources"
        return (
            f"[FAKE ANSWER] You asked: {question!r}. "
            f"Found {len(contexts)} context chunk(s) from: {sources}."
        )

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant answering questions based on provided documents.",
        },
        {
            "role": "user",
            "content": f"Based on the following documents, answer the question:\n\nDocuments:\n{context_text}\n\nQuestion: {question}",
        },
    ]

    response = client.chat.completions.create(
        model=OPENAI_CHAT_MODEL,
        messages=messages,
    )

    return response.choices[0].message.content
