def embed_texts(texts: list[str]) -> list[list[float]]:
    # TODO: Implement with actual embedding model (e.g., OpenAI, Ollama, etc.)
    # For now, return dummy embeddings
    return [[0.0] * 1536 for _ in texts]


def generate_answer(question: str, contexts: list) -> str:
    # TODO: Implement with actual LLM (e.g., OpenAI, Ollama, etc.)
    # For now, return a placeholder answer
    return f"Answer to: {question}"
