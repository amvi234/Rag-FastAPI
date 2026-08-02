# RAG FastAPI - Test Specification

## Test Overview

Comprehensive test suite covering all services and endpoints.

**Test Framework:** pytest  
**Coverage Target:** >90%  
**Location:** `/tests` directory

---

## Test Structure

```
tests/
├── conftest.py                 # Pytest fixtures and configuration
├── test_ingest.py              # Document ingestion service tests
├── test_llm.py                 # LLM service tests
├── test_vector_store.py        # Vector store service tests
├── test_main.py                # FastAPI endpoint tests
├── test_rag.py                 # RAG orchestration tests
└── fixtures/
    └── sample.pdf              # Sample PDF for integration tests
```

---

## Running Tests

### Run All Tests
```bash
uv run pytest tests/
```

### Run Specific Test File
```bash
uv run pytest tests/test_ingest.py
```

### Run Specific Test Class
```bash
uv run pytest tests/test_ingest.py::TestExtractText
```

### Run Specific Test Function
```bash
uv run pytest tests/test_ingest.py::TestExtractText::test_extract_pdf_file
```

### Run with Coverage
```bash
uv run pytest tests/ --cov=app
```

### Run with Verbose Output
```bash
uv run pytest tests/ -v
```

---

## Test Categories

### 1. Unit Tests

Unit tests verify individual functions in isolation using mocks.

#### `test_ingest.py`

**Class: TestExtractTextFromPdf**
- `test_extract_text_from_valid_pdf` - Handle valid PDF bytes
- `test_extract_text_from_pdf_empty_pages` - Handle empty pages
- `test_extract_text_from_pdf_invalid` - Raise exception for invalid PDF

**Class: TestExtractText**
- `test_extract_pdf_file` - Extract from PDF files
- `test_extract_txt_file` - Extract from TXT files
- `test_extract_markdown_file` - Extract from MD files
- `test_extract_unsupported_file_type` - Raise ValueError for unsupported types
- `test_extract_text_case_insensitive` - Handle case variations
- `test_extract_txt_with_invalid_encoding` - Handle invalid UTF-8

**Class: TestChunkText**
- `test_chunk_text_basic` - Split text into chunks
- `test_chunk_text_with_overlap` - Create overlapping chunks
- `test_chunk_text_empty` - Handle empty text
- `test_chunk_text_short` - Handle text shorter than chunk_size
- `test_chunk_text_removes_extra_whitespace` - Normalize whitespace
- `test_chunk_text_custom_parameters` - Respect custom parameters

**Class: TestIngestFile**
- `test_ingest_file_success` - Successfully ingest file (mocked)
- `test_ingest_file_with_metadata` - Verify metadata structure
- `test_ingest_empty_file` - Handle files with no content
- `test_ingest_unsupported_file_type` - Raise ValueError

#### `test_llm.py`

**Class: TestEmbedTexts**
- `test_embed_single_text` - Embed single text (mocked OpenAI)
- `test_embed_multiple_texts` - Embed multiple texts
- `test_embed_uses_correct_model` - Verify model parameter
- `test_embed_passes_correct_input` - Verify input passing
- `test_embed_empty_list` - Handle empty list

**Class: TestGenerateAnswer**
- `test_generate_answer_basic` - Generate answer (mocked)
- `test_generate_answer_with_multiple_contexts` - Include all contexts
- `test_generate_answer_uses_correct_model` - Verify model parameter
- `test_generate_answer_system_prompt` - Verify system prompt
- `test_generate_answer_question_in_prompt` - Include question
- `test_generate_answer_empty_contexts` - Handle empty contexts
- `test_generate_answer_formats_sources` - Format sources correctly

#### `test_vector_store.py`

**Class: TestUpsertDocuments**
- `test_upsert_single_document` - Upsert single document
- `test_upsert_multiple_documents` - Upsert multiple documents
- `test_upsert_with_full_metadata` - Preserve metadata
- `test_upsert_empty_lists` - Handle empty lists

**Class: TestSearchDocuments**
- `test_search_returns_documents` - Return search results
- `test_search_respects_k_parameter` - Verify k parameter
- `test_search_formats_results` - Format response correctly
- `test_search_handles_missing_metadata` - Use default values
- `test_search_passes_query_embedding` - Pass embedding correctly
- `test_search_includes_required_fields` - Request required fields
- `test_search_empty_results` - Handle empty results
- `test_search_multiple_results` - Handle multiple results

#### `test_main.py`

**Class: TestRootEndpoint**
- `test_root_returns_message` - GET / returns message
- `test_root_returns_docs_link` - GET / returns docs link

**Class: TestHealthEndpoint**
- `test_health_returns_ok` - GET /health returns ok

**Class: TestIngestEndpoint**
- `test_ingest_pdf_file` - POST /ingest PDF
- `test_ingest_txt_file` - POST /ingest TXT
- `test_ingest_calls_service` - Verify service call
- `test_ingest_returns_error_on_unsupported_type` - 400 error
- `test_ingest_returns_error_on_server_error` - 500 error
- `test_ingest_requires_file` - 422 for missing file

**Class: TestAskEndpoint**
- `test_ask_question_basic` - POST /ask with question
- `test_ask_with_custom_k` - POST /ask with custom k
- `test_ask_uses_default_k` - Use default k=4
- `test_ask_validates_k_bounds` - Reject k outside 1-10
- `test_ask_requires_question` - 422 for missing question
- `test_ask_validates_question_length` - 422 for empty question
- `test_ask_returns_error_on_exception` - 500 error
- `test_ask_returns_sources_with_metadata` - Verify sources

---

### 2. Integration Tests

Integration tests verify interaction between services without mocking dependencies.

#### Prerequisites
- OpenAI API key configured
- ChromaDB running
- Internet connectivity

#### Manual Integration Tests

**Test Case: Complete Workflow**
1. Upload a PDF file via `/ingest`
2. Verify `file_id` returned
3. Verify chunks > 0
4. Ask question via `/ask`
5. Verify answer is not empty
6. Verify sources contain chunks from uploaded document

```bash
# Upload document
curl -X POST "http://localhost:8000/ingest" \
  -F "file=@docs/sample.pdf"

# Ask question
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}'
```

**Test Case: Multiple Documents**
1. Upload 3 different documents
2. Ask question
3. Verify sources include chunks from all documents

**Test Case: Edge Cases**
- Empty PDF
- Very large document (>10MB)
- Document with special characters
- Question with special characters

---

## Fixtures

### conftest.py

#### `client`
FastAPI TestClient for making requests.

```python
def test_something(client):
    response = client.get("/health")
```

#### `mock_openai_client`
Mocked OpenAI client for tests.

```python
def test_embed(mock_openai_client):
    mock_openai_client.embeddings.create.return_value = ...
```

#### `mock_chroma_collection`
Mocked ChromaDB collection.

```python
def test_search(mock_chroma_collection):
    mock_chroma_collection.query.return_value = ...
```

#### `sample_pdf_bytes`
Sample PDF file bytes for testing.

#### `sample_text`
Sample text string for chunking tests.

#### `sample_embedding`
Sample embedding vector (1536 dimensions).

---

## Mock Strategy

### Unit Tests (Mocking)
- Mock OpenAI API calls
- Mock ChromaDB collection
- Use real text processing functions

### Benefits
- Fast execution (no API calls)
- No API costs
- Isolated from external dependencies
- Deterministic results

### Example
```python
@patch("app.services.llm.client")
def test_embed_texts(self, mock_client):
    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=[0.1] * 1536)]
    mock_client.embeddings.create.return_value = mock_response
    
    result = embed_texts(["Hello"])
    assert len(result) == 1
```

---

## Test Data

### Minimal PDF
Used in `sample_pdf_bytes` fixture for basic PDF parsing tests.

### Sample Text
```
"This is a sample document about machine learning and artificial intelligence."
```

### Sample Embedding
Vector of 1536 floats: `[0.1] * 1536`

---

## Error Cases Covered

| Error Case | Test Location | Verification |
|-----------|---------------|--------------|
| Unsupported file type | `test_ingest.py::TestExtractText::test_extract_unsupported_file_type` | Raises ValueError |
| Empty question | `test_main.py::TestAskEndpoint::test_ask_validates_question_length` | Returns 422 |
| k out of bounds | `test_main.py::TestAskEndpoint::test_ask_validates_k_bounds` | Returns 422 |
| Invalid PDF | `test_ingest.py::TestExtractTextFromPdf::test_extract_text_from_pdf_invalid` | Raises Exception |
| Missing file | `test_main.py::TestIngestEndpoint::test_ingest_requires_file` | Returns 422 |
| Server error | `test_main.py::TestIngestEndpoint::test_ingest_returns_error_on_server_error` | Returns 500 |
| Empty file | `test_ingest.py::TestIngestFile::test_ingest_empty_file` | Returns 0 chunks |

---

## Test Execution Timeline

### Fast Tests (< 1 second)
- All unit tests with mocks
- Text extraction and chunking tests

### Medium Tests (1-5 seconds)
- API endpoint tests
- Service orchestration tests

### Slow Tests (5+ seconds)
- Integration tests with real OpenAI API
- Real ChromaDB operations

---

## Continuous Integration

### Pre-commit Testing
```bash
uv run pytest tests/ --tb=short -q
```

### CI/CD Pipeline
```bash
uv run pytest tests/ --cov=app --cov-report=term-missing
```

---

## Coverage Goals

| Component | Target | Current |
|-----------|--------|---------|
| app/main.py | 100% | - |
| app/services/config.py | 90% | - |
| app/services/ingest.py | 100% | - |
| app/services/llm.py | 100% | - |
| app/services/vector_store.py | 100% | - |
| app/services/rag.py | 100% | - |
| **Total** | **>90%** | - |

---

## Known Limitations

1. **OpenAI API Mocking**
   - Tests do not call real OpenAI API
   - Integration tests required for real API validation

2. **ChromaDB Mocking**
   - Tests do not test actual vector search quality
   - Real ChromaDB operations should be tested separately

3. **File Handling**
   - Large file tests not implemented
   - Network timeout tests not implemented

---

## Future Test Cases

- [ ] Performance benchmarks
- [ ] Load testing (concurrent requests)
- [ ] Real OpenAI API integration tests
- [ ] ChromaDB persistence tests
- [ ] Memory leak detection
- [ ] PDF parsing edge cases (scanned images, non-Latin text)
