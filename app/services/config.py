import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# "openai" (default) hits the real API. "fake" returns deterministic stub
# data from app/services/llm.py so you can exercise /ingest and /ask without
# any network calls or API key.
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-5.5")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "rag_docs")

BASE_DIR = Path(__file__).resolve().parents[2]

if LLM_PROVIDER == "openai" and not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing. Add it to your .env file.")