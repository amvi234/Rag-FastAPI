from app.services.llm import embed_texts, generate_answer
from app.services.vector_store import search_documents


def answer_question(question: str, k: int = 4) -> dict:
    query_embedding = embed_texts([question])[0]

    contexts = search_documents(
        query_embedding=query_embedding,
        k=k,
    )

    answer = generate_answer(
        question=question,
        contexts=contexts,
    )

    return {
        "question": question,
        "answer": answer,
        "sources": contexts,
    }