# RAG FastAPI - Service Specification

## Services Overview

This document defines the specifications for all services in the RAG pipeline.

---

## 1. Config Service (`app/services/config.py`)

Manages environment configuration and constants.

### Exports

#### `OPENAI_API_KEY`
- **Type:** `str`
- **Description:** OpenAI API key for authentication
- **Source:** Environment variable
- **Required:** Yes
- **Raises:** `RuntimeError` if not set

#### `OPENAI_CHAT_MODEL`
- **Type:** `str`
- **Description:** OpenAI model for chat/answer generation
- **Default:** `gpt-5.5`
- **Source:** Environment variable `OPENAI_CHAT_MODEL`

#### `OPENAI_EMBEDDING_MODEL`
- **Type:** `str`
- **Description:** OpenAI model for text embeddings
- **Default:** `text-embedding-3-small`
- **Source:** Environment variable `OPENAI_EMBEDDING_MODEL`

#### `CHROMA_PATH`
- **Type:** `str`
- **Description:** Directory path for ChromaDB persistence
- **Default:** `./chroma`
- **Source:** Environment variable `CHROMA_PATH`

#### `COLLECTION_NAME`
- **Type:** `str`
- **Description:** Name of ChromaDB collection for storing documents
- **Default:** `rag_docs`
- **Source:** Environment variable `COLLECTION_NAME`

#### `BASE_DIR`
- **Type:** `Path`
- **Description:** Root directory of the project
- **Derived:** Parent of parent directory of config.py

---

## 2. Ingest Service (`app/services/ingest.py`)

Handles document ingestion, text extraction, and chunking.

### Functions

#### `extract_text_from_pdf(file_bytes: bytes) -> str`

Extracts text from PDF file bytes.

**Parameters:**
- `file_bytes` (bytes): Raw PDF file content

**Returns:**
- `str`: Concatenated text from all PDF pages, joined with newlines

**Raises:**
- `Exception`: If PDF is invalid or corrupted

**Implementation Details:**
- Uses `pypdf.PdfReader` to parse PDF
- Iterates through all pages
- Handles missing text gracefully (returns empty string per page)
- Joins pages with `\n`

---

#### `extract_text(filename: str, file_bytes: bytes) -> str`

Extracts text based on file extension.

**Parameters:**
- `filename` (str): Original filename with extension
- `file_bytes` (bytes): Raw file content

**Returns:**
- `str`: Extracted text content

**Raises:**
- `ValueError`: If file extension is not `.pdf`, `.txt`, or `.md`

**Behavior by Extension:**
- `.pdf`: Calls `extract_text_from_pdf()`
- `.txt`, `.md`: Decodes as UTF-8 with errors ignored
- Other: Raises ValueError

**Notes:**
- Extension matching is case-insensitive
- UTF-8 decoding uses `errors="ignore"` for robustness

---

#### `chunk_text(text: str, chunk_size: int = 1200, overlap: int = 200) -> list[str]`

Splits text into overlapping chunks.

**Parameters:**
- `text` (str): Text content to chunk
- `chunk_size` (int): Target characters per chunk (default: 1200)
- `overlap` (int): Character overlap between chunks (default: 200)

**Returns:**
- `list[str]`: List of text chunks, each stripped of whitespace

**Algorithm:**
1. Normalize whitespace (collapse multiple spaces/newlines)
2. Iterate with sliding window: `start += chunk_size - overlap`
3. Extract window of `chunk_size` characters
4. Only include non-empty (after stripping) chunks

**Example:**
```
Text: "a" * 2400, chunk_size=1200, overlap=200
Result: 2 chunks of ~1200 chars with 200 char overlap
```

---

#### `ingest_file(filename: str, file_bytes: bytes) -> dict`

Complete ingestion pipeline for a document.

**Parameters:**
- `filename` (str): Original filename
- `file_bytes` (bytes): Raw file content

**Returns:**
```json
{
  "filename": "string",
  "file_id": "string (UUID4)",
  "chunks": "integer",
  "message": "string"
}
```

**Process:**
1. Extract text from file
2. Split text into chunks
3. Generate embeddings for each chunk
4. Create file_id (UUID4)
5. Build metadata for each chunk (source, chunk_index, file_id)
6. Upsert to vector store

**Response on Success:**
```json
{
  "filename": "document.pdf",
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "chunks": 12,
  "message": "File ingested successfully."
}
```

**Response on Empty File:**
```json
{
  "filename": "empty.txt",
  "chunks": 0,
  "message": "No text found in file."
}
```

**Raises:**
- `ValueError`: If file type is unsupported

---

## 3. LLM Service (`app/services/llm.py`)

Interfaces with OpenAI API for embeddings and answer generation.

### Dependencies
- `openai.OpenAI` client
- Config service for API key and model names

### Functions

#### `embed_texts(texts: list[str]) -> list[list[float]]`

Generates embeddings for text strings using OpenAI.

**Parameters:**
- `texts` (list[str]): List of text strings to embed

**Returns:**
- `list[list[float]]`: List of embedding vectors
  - Each embedding is a list of 1536 floats (for text-embedding-3-small)
  - Order matches input order

**API Call:**
```
POST https://api.openai.com/v1/embeddings
Model: text-embedding-3-small
```

**Example:**
```python
embeddings = embed_texts(["Hello world", "AI is great"])
# Returns: [[0.001, -0.002, ...], [0.003, -0.001, ...]]
```

**Raises:**
- OpenAI API errors (authentication, rate limit, etc.)

---

#### `generate_answer(question: str, contexts: list) -> str`

Generates an answer to a question using retrieved context.

**Parameters:**
- `question` (str): User's question
- `contexts` (list): List of context documents from vector search
  - Each context: `{"text": str, "source": str, "chunk_index": int, "distance": float}`

**Returns:**
- `str`: Generated answer text

**Prompt Structure:**
1. **System Message:** "You are a helpful assistant answering questions based on provided documents."
2. **User Message:** Formatted with contexts and question

**Context Formatting:**
```
Documents:
Source: document.pdf
[chunk text]

Source: document.txt
[chunk text]

Question: [user question]
```

**API Call:**
```
POST https://api.openai.com/v1/chat/completions
Model: gpt-5.5 (configurable)
Messages: [system, user]
```

**Example:**
```python
contexts = [{"text": "AI is...", "source": "doc.pdf"}]
answer = generate_answer("What is AI?", contexts)
# Returns: "AI is artificial intelligence..."
```

**Raises:**
- OpenAI API errors (authentication, rate limit, etc.)

---

## 4. Vector Store Service (`app/services/vector_store.py`)

Interfaces with ChromaDB for document storage and retrieval.

### Module-level Code
- Creates persistent ChromaDB client at `CHROMA_PATH`
- Initializes or retrieves collection `COLLECTION_NAME` with cosine similarity

### Functions

#### `upsert_documents(ids: list[str], documents: list[str], embeddings: list[list[float]], metadatas: list[dict]) -> None`

Stores documents and embeddings in vector database.

**Parameters:**
- `ids` (list[str]): Unique identifiers for documents
  - Format: `{file_id}-{chunk_index}`
- `documents` (list[str]): Text content of each document
- `embeddings` (list[list[float]]): Embedding vectors for each document
- `metadatas` (list[dict]): Metadata for each document
  - Expected fields: `source`, `chunk_index`, `file_id`

**Returns:**
- `None`

**Side Effects:**
- Writes documents to ChromaDB collection
- Overwrites existing documents with same id

**Metadata Example:**
```json
{
  "source": "document.pdf",
  "chunk_index": 0,
  "file_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

#### `search_documents(query_embedding: list[float], k: int = 4) -> list[dict]`

Retrieves most similar documents from vector store.

**Parameters:**
- `query_embedding` (list[float]): Query embedding vector
- `k` (int): Number of results to return (default: 4)

**Returns:**
```python
[
  {
    "text": "chunk content",
    "source": "filename",
    "chunk_index": 0,
    "distance": 0.12
  },
  ...
]
```

**ChromaDB Query:**
```
Query Mode: Similarity search
Space: Cosine distance
Include: documents, metadatas, distances
n_results: k
```

**Distance Score:**
- 0.0 = identical (perfect match)
- 1.0 = completely different
- Lower values indicate more similar documents

**Default Values:**
- Missing `source` → "unknown"
- Missing `chunk_index` → -1

**Raises:**
- ChromaDB errors (connection, invalid embedding, etc.)

---

## 5. RAG Service (`app/services/rag.py`)

Orchestrates the RAG pipeline: embedding, search, and answer generation.

### Functions

#### `answer_question(question: str, k: int = 4) -> dict`

Answers a question by retrieving relevant documents and generating an answer.

**Parameters:**
- `question` (str): User's question
- `k` (int): Number of document chunks to retrieve (default: 4)

**Returns:**
```json
{
  "question": "What is AI?",
  "answer": "AI is artificial intelligence...",
  "sources": [
    {
      "text": "...",
      "source": "doc.pdf",
      "chunk_index": 0,
      "distance": 0.12
    }
  ]
}
```

**Process:**
1. Embed the question using `embed_texts()`
2. Search for similar documents using `search_documents()`
3. Generate answer using `generate_answer()`
4. Return structured response

**Side Effects:**
- No modifications to database

**Raises:**
- OpenAI API errors
- ChromaDB errors

---

## Environment Variables

| Variable | Default | Required | Example |
|----------|---------|----------|---------|
| `OPENAI_API_KEY` | N/A | Yes | `sk-proj-...` |
| `OPENAI_CHAT_MODEL` | `gpt-5.5` | No | `gpt-4-turbo` |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | No | `text-embedding-3-large` |
| `CHROMA_PATH` | `./chroma` | No | `/data/chroma` |
| `COLLECTION_NAME` | `rag_docs` | No | `my_documents` |

---

## Data Flow

```
Document Upload
    ↓
extract_text() → text
    ↓
chunk_text() → chunks[]
    ↓
embed_texts() → embeddings[]
    ↓
upsert_documents() → ChromaDB
    ↓
Vector Store Ready

User Question
    ↓
embed_texts() → query_embedding
    ↓
search_documents() → contexts[]
    ↓
generate_answer() → answer
    ↓
Response
```

---

## Error Handling Strategy

### Critical Errors (Halt)
- Missing `OPENAI_API_KEY` → Raise RuntimeError at startup
- Invalid PDF → Re-raise Exception from pypdf
- Unsupported file type → Raise ValueError

### Recoverable Errors (Log & Continue)
- Invalid UTF-8 in TXT → Ignore with `errors="ignore"`
- Empty pages in PDF → Return empty string
- Empty text after extraction → Return response with 0 chunks
- OpenAI API errors → Propagate to caller for HTTP error response

---

## Performance Characteristics

### Ingest (`ingest_file`)
- **Time Complexity:** O(n) where n = file size
- **OpenAI API Calls:** 1 (for embeddings)
- **ChromaDB Calls:** 1 (upsert)
- **Typical Duration:** 2-5 seconds per document

### Query (`answer_question`)
- **Time Complexity:** O(1) for search + O(1) for answer generation
- **OpenAI API Calls:** 2 (embed query + generate answer)
- **ChromaDB Calls:** 1 (search)
- **Typical Duration:** 1-3 seconds per question
