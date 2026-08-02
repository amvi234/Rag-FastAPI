# RAG FastAPI - Setup Guide

## Prerequisites

- Python 3.12+
- OpenAI API key
- Internet connection (for OpenAI API calls)

---

## 1. Get OpenAI API Key

### Step-by-Step

1. **Create/Login to OpenAI Account**
   - Go to https://platform.openai.com/signup
   - Sign up or log in

2. **Generate API Key**
   - Navigate to https://platform.openai.com/api-keys
   - Click **"Create new secret key"**
   - Copy the key (you can only see it once!)

3. **Example Key Format**
   ```
   sk-proj-AbCdEfGhIjKlMnOpQrStUvWxYz123456789...
   ```

4. **Save Securely**
   - Do not share this key
   - Do not commit to version control
   - Consider using a password manager

---

## 2. Configure Environment Variables

### Option A: Update .env File (Recommended for Development)

1. **Copy template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit .env file:**
   ```bash
   # On Linux/Mac
   nano .env
   
   # On Windows (VS Code)
   code .env
   ```

3. **Replace placeholder with your API key:**
   ```bash
   # Before:
   OPENAI_API_KEY=sk-proj-your_key_here

   # After:
   OPENAI_API_KEY=sk-proj-AbCdEfGhIjKlMnOpQrStUvWxYz123456789...
   ```

4. **Optional: Update model choices**
   ```bash
   # For development (cheaper):
   OPENAI_CHAT_MODEL=gpt-3.5-turbo
   OPENAI_EMBEDDING_MODEL=text-embedding-3-small

   # For production (better quality):
   OPENAI_CHAT_MODEL=gpt-4-turbo
   OPENAI_EMBEDDING_MODEL=text-embedding-3-large
   ```

### Option B: Environment Variables (For Docker/Production)

```bash
# Export in your shell
export OPENAI_API_KEY=sk-proj-xxx
export OPENAI_CHAT_MODEL=gpt-4-turbo
export OPENAI_EMBEDDING_MODEL=text-embedding-3-small
export CHROMA_PATH=./chroma
export COLLECTION_NAME=rag_docs
```

### Option C: Docker Environment (In docker-compose.yml)

```yaml
services:
  api:
    environment:
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      OPENAI_CHAT_MODEL: gpt-4-turbo
      OPENAI_EMBEDDING_MODEL: text-embedding-3-small
      CHROMA_PATH: /data/chroma
      COLLECTION_NAME: rag_docs
```

---

## 3. Verify Setup

### Check Configuration
```bash
# The app will validate on startup
uv run fastapi dev app/main.py
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

If you see:
```
RuntimeError: OPENAI_API_KEY is missing. Add it to your .env file.
```

Then API key is not configured correctly.

### Test Health Endpoint
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "ok"}
```

### Test with Documentation
- Open http://localhost:8000/docs
- Try uploading a document and asking a question

---

## 4. Project Structure

```
rag-fastapi/
├── .env                  # ← Your configuration (DO NOT commit)
├── .env.example         # ← Template (COMMIT this)
├── .gitignore           # ← .env should be ignored
├── app/
│   ├── main.py          # FastAPI app and endpoints
│   └── services/
│       ├── config.py    # ← Loads .env variables
│       ├── ingest.py    # Document ingestion
│       ├── llm.py       # OpenAI API calls
│       ├── rag.py       # RAG orchestration
│       └── vector_store.py  # ChromaDB interface
├── docs/
│   ├── API_SPEC.md      # API endpoints
│   ├── SERVICE_SPEC.md  # Service specifications
│   ├── CONFIG_SPEC.md   # Configuration details
│   ├── TEST_SPEC.md     # Test specifications
│   └── SETUP_GUIDE.md   # This file
├── tests/               # Test suite
├── chroma/              # Vector database (created by app)
├── data/                # Sample data
└── pyproject.toml       # Dependencies
```

---

## 5. First Time Run

### 1. Install Dependencies
```bash
uv sync
```

### 2. Configure API Key
```bash
cp .env.example .env
# Edit .env with your actual API key
```

### 3. Start Server
```bash
uv run fastapi dev app/main.py
```

### 4. Upload a Document
```bash
# Create a test file
echo "Artificial Intelligence is the simulation of human intelligence by machines." > sample.txt

# Upload it
curl -X POST "http://localhost:8000/ingest" \
  -F "file=@sample.txt"
```

Expected response:
```json
{
  "filename": "sample.txt",
  "file_id": "550e8400-e29b-41d4-a716-446655440000",
  "chunks": 1,
  "message": "File ingested successfully."
}
```

### 5. Ask a Question
```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is AI?"}'
```

Expected response:
```json
{
  "question": "What is AI?",
  "answer": "Artificial Intelligence (AI) is the simulation of human intelligence by machines...",
  "sources": [
    {
      "text": "Artificial Intelligence is the simulation of human intelligence by machines.",
      "source": "sample.txt",
      "chunk_index": 0,
      "distance": 0.05
    }
  ]
}
```

---

## 6. OpenAI Pricing

### Chat Models
| Model | Input (1K tokens) | Output (1K tokens) |
|-------|-------------------|-------------------|
| gpt-3.5-turbo | $0.0005 | $0.0015 |
| gpt-4-turbo | $0.01 | $0.03 |
| gpt-4o | $0.005 | $0.015 |

### Embedding Models
| Model | Cost (1M tokens) |
|-------|-----------------|
| text-embedding-3-small | $0.02 |
| text-embedding-3-large | $0.13 |

### Cost Estimation
- **Per document ingest:** 1 embedding call = cost of 1 document
- **Per question:** 2 calls (embed question + generate answer) = ~$0.01-0.10

---

## 7. Troubleshooting

### Issue: "RuntimeError: OPENAI_API_KEY is missing"

**Solution:**
```bash
# Check if .env exists
ls -la .env

# Check if key is set
cat .env | grep OPENAI_API_KEY

# Verify no spaces around =
# Should be: OPENAI_API_KEY=sk-proj-xxx
# NOT: OPENAI_API_KEY = sk-proj-xxx
```

### Issue: "Invalid API key provided"

**Solution:**
```bash
# Verify your key is valid at: https://platform.openai.com/api-keys
# Check key format: must start with sk-proj-
# Test with curl:
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_KEY_HERE" | head -20
```

### Issue: "Model 'gpt-5.5' not found"

**Solution:**
```bash
# gpt-5.5 might be a placeholder
# Update .env with actual model name:
OPENAI_CHAT_MODEL=gpt-4-turbo

# Or use gpt-3.5-turbo for cheaper development
OPENAI_CHAT_MODEL=gpt-3.5-turbo
```

### Issue: "Rate limit exceeded"

**Solution:**
- Upgrade OpenAI plan at https://platform.openai.com/account/billing/overview
- Implement request throttling/caching
- Use gpt-3.5-turbo instead of gpt-4-turbo

---

## 8. Next Steps

1. **Run Tests**
   ```bash
   uv run pytest tests/ -v
   ```

2. **Read Documentation**
   - API endpoints: `docs/API_SPEC.md`
   - Services: `docs/SERVICE_SPEC.md`
   - Configuration: `docs/CONFIG_SPEC.md`
   - Tests: `docs/TEST_SPEC.md`

3. **Explore FastAPI Docs**
   - Interactive: http://localhost:8000/docs
   - Alternative: http://localhost:8000/redoc

4. **Customize Models**
   - Update model names in `.env`
   - See CONFIG_SPEC.md for options

5. **Deploy**
   - Docker: See Dockerfile recommendations
   - Cloud: AWS Lambda, Google Cloud Run, Azure Functions, etc.
   - VPS: Follow production deployment guide

---

## 10. Getting Help

### API Documentation
- See `docs/API_SPEC.md` for endpoint specifications
- Try interactive docs at http://localhost:8000/docs

### Service Documentation
- See `docs/SERVICE_SPEC.md` for detailed function specs

### Test Examples
- See `tests/` directory for usage examples

### OpenAI Documentation
- Models: https://platform.openai.com/docs/models
- Embeddings: https://platform.openai.com/docs/guides/embeddings
- Chat: https://platform.openai.com/docs/guides/chat-completions
