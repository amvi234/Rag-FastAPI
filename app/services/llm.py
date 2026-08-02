from openai import OpenAI

from app.services.config import OPENAI_API_KEY, OPENAI_CHAT_MODEL, OPENAI_EMBEDDING_MODEL

client = OpenAI(api_key=OPENAI_API_KEY)


def embed_texts(texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(
        model=OPENAI_EMBEDDING_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]


def generate_answer(question: str, contexts: list) -> str:
    context_text = "\n\n".join(
        [f"Source: {ctx['source']}\n{ctx['text']}" for ctx in contexts]
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
