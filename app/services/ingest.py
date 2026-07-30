import io
import uuid
from pathlib import Path

from pypdf import PdfReader

from app.services.llm import embed_texts
from app.services.vector_store import upsert_documents


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))

    pages = []

    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)

    return "\n".join(pages)


def extract_text(filename: str, file_bytes: bytes) -> str:
    suffix = Path(filename).suffix.lower()

    if suffix == ".pdf":
        return extract_text_from_pdf(file_bytes)

    if suffix in [".txt", ".md"]:
        return file_bytes.decode("utf-8", errors="ignore")

    raise ValueError("Unsupported file type. Please upload .pdf, .txt, or .md files.")


def chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> list[str]:
    """
    Simple character-based chunking.
    Later, you can replace this with token-based chunking.
    """

    text = " ".join(text.split())

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk.strip())

        start += chunk_size - overlap

    return chunks


def ingest_file(filename: str, file_bytes: bytes) -> dict:
    text = extract_text(filename, file_bytes)

    chunks = chunk_text(text)

    if not chunks:
        return {
            "filename": filename,
            "chunks": 0,
            "message": "No text found in file.",
        }

    embeddings = embed_texts(chunks)

    file_id = str(uuid.uuid4())

    ids = []
    metadatas = []

    for index, _chunk in enumerate(chunks):
        ids.append(f"{file_id}-{index}")
        metadatas.append(
            {
                "source": filename,
                "chunk_index": index,
                "file_id": file_id,
            }
        )

    upsert_documents(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return {
        "filename": filename,
        "file_id": file_id,
        "chunks": len(chunks),
        "message": "File ingested successfully.",
    }