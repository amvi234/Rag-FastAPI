import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_CHAT_MODEL = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.8-flash")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")

CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "rag_docs")

BASE_DIR = Path(__file__).resolve().parents[2]
