# RAG FastAPI - API Specification

## Overview
FastAPI RAG project provides REST endpoints for document ingestion and question answering using Retrieval-Augmented Generation (RAG) with OpenAI models and ChromaDB vector storage.

**Base URL:** `http://localhost:8000`

**Version:** 0.1.0

---

## Endpoints

### 1. Health Check
**GET** `/health`

Check if the service is running.

**Response:**
```json
{
  "status": "ok"
}
```

**Status Code:** 200 OK

---

### 2. Root
**GET** `/`

Get welcome message and documentation link.

**Response:**
```json
{
  "message": "FastAPI RAG project is running.",
  "docs": "/docs"
}
```

**Status Code:** 200 OK

---

### 3. Ingest Document
**POST** `/ingest`

Upload and ingest a document for RAG processing.

**Request:**
- **Content-Type:** `multipart/form-data`
- **Parameters:**
  - `file` (required, file): PDF, TXT, or MD file

**Supported File Types:**
- `.pdf` - PDF documents
- `.txt` - Plain text files
- `.md` - Markdown files

**Response (Success):**
```json
{
  "filename": "document.pdf",
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "chunks": 12,
  "message": "File ingested successfully."
}
```

**Response Fields:**
- `filename`: Original uploaded filename
- `file_id`: Unique identifier for the ingested document
- `chunks`: Number of text chunks created from the document
- `message`: Status message

**Status Codes:**
- `200 OK` - Successfully ingested
- `400 Bad Request` - Unsupported file type or invalid file
- `500 Internal Server Error` - Server error during ingestion

**Error Response (400):**
```json
{
  "detail": "Unsupported file type. Please upload .pdf, .txt, or .md files."
}
```

**Error Response (500):**
```json
{
  "detail": "Error message describing what went wrong"
}
```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/ingest" \
  -F "file=@document.pdf"
```

---

### 4. Ask Question
**POST** `/ask`

Ask a question about ingested documents.

**Request:**
```json
{
  "question": "What is machine learning?",
  "k": 4
}
```

**Request Fields:**
- `question` (required, string): The question to ask
  - Minimum length: 1 character
  - Maximum length: no limit (recommended < 500 chars)
- `k` (optional, integer): Number of document chunks to retrieve
  - Default: 4
  - Minimum: 1
  - Maximum: 10

**Response (Success):**
```json
{
  "question": "What is machine learning?",
  "answer": "Machine learning is a subset of artificial intelligence...",
  "sources": [
    {
      "text": "Machine learning is the study of computer algorithms...",
      "source": "document.pdf",
      "chunk_index": 0,
      "distance": 0.12
    },
    {
      "text": "ML models learn from data without being explicitly programmed...",
      "source": "document.pdf",
      "chunk_index": 5,
      "distance": 0.18
    }
  ]
}
```

**Response Fields:**
- `question`: The question that was asked
- `answer`: Generated answer from OpenAI model
- `sources`: Array of relevant document chunks used to generate the answer
  - `text`: The actual chunk content
  - `source`: Source file name
  - `chunk_index`: Position of chunk in the document
  - `distance`: Semantic similarity score (lower is more similar)

**Status Codes:**
- `200 OK` - Successfully answered
- `422 Unprocessable Entity` - Invalid request parameters
- `500 Internal Server Error` - Server error during processing

**Error Response (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "question"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.str.min_length"
    }
  ]
}
```

**Error Response (500):**
```json
{
  "detail": "Error message describing what went wrong"
}
```

**Example cURL:**
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is machine learning?",
    "k": 5
  }'
```

---

## Request/Response Data Types

### AskRequest
```json
{
  "question": "string (required, min_length=1)",
  "k": "integer (optional, default=4, range=1-10)"
}
```

### IngestResponse
```json
{
  "filename": "string",
  "file_id": "string (UUID format)",
  "chunks": "integer",
  "message": "string"
}
```

### AskResponse
```json
{
  "question": "string",
  "answer": "string",
  "sources": [
    {
      "text": "string",
      "source": "string",
      "chunk_index": "integer",
      "distance": "float"
    }
  ]
}
```

### HealthResponse
```json
{
  "status": "string"
}
```

---

## Error Handling

### HTTP Status Codes
- **200 OK** - Request successful
- **400 Bad Request** - Unsupported file type or invalid input
- **422 Unprocessable Entity** - Validation error in request body
- **500 Internal Server Error** - Unexpected server error

### Common Errors

**Unsupported File Type**
```
Status: 400
{"detail": "Unsupported file type. Please upload .pdf, .txt, or .md files."}
```

**Empty Question**
```
Status: 422
{"detail": "ensure this value has at least 1 characters"}
```

**Invalid k Parameter**
```
Status: 422
{"detail": "ensure this value is less than or equal to 10"}
```

**No Documents Ingested**
```
Status: 200
{
  "answer": "Answer to: [question]",
  "sources": []
}
```

---

## Workflow Example

### 1. Upload Document
```bash
curl -X POST "http://localhost:8000/ingest" \
  -F "file=@research_paper.pdf"
```

**Response:**
```json
{
  "filename": "research_paper.pdf",
  "file_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "chunks": 25,
  "message": "File ingested successfully."
}
```

### 2. Ask Question
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What are the main findings?",
    "k": 5
  }'
```

**Response:**
```json
{
  "question": "What are the main findings?",
  "answer": "According to the research paper, the main findings include...",
  "sources": [
    {
      "text": "Our analysis reveals three key findings...",
      "source": "research_paper.pdf",
      "chunk_index": 12,
      "distance": 0.08
    }
  ]
}
```

---

## Rate Limiting
Currently no rate limiting is implemented.

---

## Authentication
Currently no authentication is required.

---

## CORS
Currently CORS is not explicitly configured. Requests from any origin are allowed.

---

## Documentation
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
