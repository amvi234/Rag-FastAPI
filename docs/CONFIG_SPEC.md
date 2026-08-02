# RAG FastAPI - Configuration Specification

## Overview

Configuration is managed through environment variables defined in `.env` file using `python-dotenv`.

---

## Environment Variables

### OPENAI_API_KEY
**Required:** Yes  
**Type:** String  
**Format:** OpenAI API key (starts with `sk-proj-`)  
**Example:**
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**How to Obtain:**
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key (you can only see it once)
4. Paste into `.env` file

**What Happens:**
- If missing or empty: Application raises `RuntimeError` at startup
- Config validation happens before server starts

**Security Notes:**
- Never commit `.env` to version control
- `.gitignore` should include `.env`
- Use `.env.example` to document required variables

---

### OPENAI_CHAT_MODEL
**Required:** No  
**Type:** String  
**Default:** `gpt-5.5`  
**Example:**
```
OPENAI_CHAT_MODEL=gpt-4-turbo
```

**Available Models:**
| Model | Description | Cost | Speed | Quality |
|-------|-------------|------|-------|---------|
| `gpt-4-turbo` | Latest GPT-4 variant | Higher | Medium | Excellent |
| `gpt-4o` | Optimized model | High | Fast | Excellent |
| `gpt-3.5-turbo` | Fast, cost-effective | Low | Fast | Good |
| `gpt-5.5` | Custom or future model | TBD | TBD | TBD |

**Impact:**
- Used by `generate_answer()` function
- Affects answer quality and cost

**Recommendations:**
- **Development:** `gpt-3.5-turbo` (lowest cost)
- **Production:** `gpt-4-turbo` or `gpt-4o` (best quality)
- **Testing:** Mock the API, no model needed

---

### OPENAI_EMBEDDING_MODEL
**Required:** No  
**Type:** String  
**Default:** `text-embedding-3-small`  
**Example:**
```
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
```

**Available Models:**
| Model | Dimensions | Cost | Speed | Quality |
|-------|-----------|------|-------|---------|
| `text-embedding-3-small` | 1536 | Low | Fast | Good |
| `text-embedding-3-large` | 3072 | Higher | Slow | Better |
| `text-embedding-ada-002` | 1536 | Medium | Medium | Good |

**Impact:**
- Used by `embed_texts()` function
- Affects document retrieval accuracy and vector store size
- 1536 dimensions = ~6KB per embedding
- 3072 dimensions = ~12KB per embedding

**Recommendations:**
- **Development/Testing:** `text-embedding-3-small` (fast, cheap)
- **Production:** `text-embedding-3-large` (better accuracy)

---

### CHROMA_PATH
**Required:** No  
**Type:** Path string  
**Default:** `./chroma`  
**Example:**
```
CHROMA_PATH=./chroma
CHROMA_PATH=/data/chroma
CHROMA_PATH=/var/lib/rag/chroma
```

**Behavior:**
- Directory where ChromaDB stores vector data persistently
- Created automatically if it doesn't exist
- Should have sufficient disk space for embeddings

**Path Types:**
- **Relative:** `./chroma` (relative to project root)
- **Absolute:** `/data/chroma` (full path)

**Disk Space Calculation:**
```
Size per embedding = 1536 floats × 4 bytes = ~6KB
Size for 1000 documents (10 chunks each) = 1000 × 10 × 6KB = ~60MB
Size for 100,000 documents = ~6GB
```

**Recommendations:**
- **Development:** `./chroma` in project directory
- **Production:** Separate data volume, e.g., `/data/chroma`
- **Docker:** Map volume to persistent storage

---

### COLLECTION_NAME
**Required:** No  
**Type:** String  
**Default:** `rag_docs`  
**Example:**
```
COLLECTION_NAME=rag_docs
COLLECTION_NAME=my_documents
COLLECTION_NAME=product_docs_v1
```

**Behavior:**
- Name of ChromaDB collection (namespace)
- Multiple collections can exist in same ChromaDB instance
- Single collection used per application instance

**Use Cases:**
- **Multi-tenant:** Different collection per tenant
- **Versioning:** Different collections for document versions
- **Testing:** Separate test collection

**Collection Metadata:**
```python
{
  "hnsw:space": "cosine"  # Similarity metric
}
```

**Recommendations:**
- Keep as `rag_docs` unless you have multiple collections
- Use descriptive names for multi-collection setups
- Version collections if updating documents: `rag_docs_v1`, `rag_docs_v2`

---

## .env File Format

### Complete Example
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_CHAT_MODEL=gpt-4-turbo
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# ChromaDB Configuration
CHROMA_PATH=./chroma
COLLECTION_NAME=rag_docs
```

### .env.example Template
```bash
# Copy this file to .env and fill in actual values

# OpenAI API Configuration (Required)
# Get API key from https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-your_key_here

# OpenAI Model Selection (Optional)
# For chat/answer generation (default: gpt-5.5)
# Options: gpt-4-turbo, gpt-4o, gpt-3.5-turbo, gpt-4, gpt-4-32k
OPENAI_CHAT_MODEL=gpt-5.5

# For text embeddings (default: text-embedding-3-small)
# Options: text-embedding-3-small, text-embedding-3-large, text-embedding-ada-002
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# ChromaDB Configuration (Optional)
# Path to store vector database (default: ./chroma)
CHROMA_PATH=./chroma

# Collection name for documents (default: rag_docs)
COLLECTION_NAME=rag_docs
```

---

## Configuration Loading Process

### 1. File Reading
```python
from dotenv import load_dotenv
load_dotenv()  # Reads .env file
```

### 2. Variable Extraction
```python
import os
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_CHAT_MODEL = os.getenv("OPENAI_CHAT_MODEL", "gpt-5.5")
```

### 3. Validation
```python
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is missing. Add it to your .env file.")
```

### 4. Usage
```python
from app.services.config import OPENAI_API_KEY, OPENAI_CHAT_MODEL
```

---

## Environment-Specific Configurations

### Development
```bash
OPENAI_API_KEY=sk-proj-xxx
OPENAI_CHAT_MODEL=gpt-3.5-turbo          # Cheap
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
CHROMA_PATH=./chroma
COLLECTION_NAME=rag_docs_dev
```

### Testing
```bash
OPENAI_API_KEY=test-key-not-used-with-mocks
OPENAI_CHAT_MODEL=gpt-5.5
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
CHROMA_PATH=./chroma_test
COLLECTION_NAME=rag_docs_test
```

### Production
```bash
OPENAI_API_KEY=sk-proj-xxx-production    # Real key
OPENAI_CHAT_MODEL=gpt-4-turbo            # Best quality
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
CHROMA_PATH=/data/chroma                 # External volume
COLLECTION_NAME=rag_docs_prod
```

---

## Configuration Management Best Practices

### 1. Version Control
```bash
# .gitignore - DO include
.env
.env.local
.env.*.local

# DO commit
.env.example
```

### 2. Secrets Management
- Never share `.env` file
- For production, use secrets manager:
  - AWS Secrets Manager
  - Azure Key Vault
  - HashiCorp Vault
  - Docker Secrets

### 3. Local Override
Create `.env.local` for local overrides (ignored by git):
```bash
# .env
OPENAI_CHAT_MODEL=gpt-4-turbo

# .env.local (local override)
OPENAI_CHAT_MODEL=gpt-3.5-turbo
```

### 4. Documentation
Document all variables in `.env.example` with comments.

---

## Troubleshooting

### Error: "OPENAI_API_KEY is missing"
**Solution:**
1. Check if `.env` file exists in project root
2. Add `OPENAI_API_KEY=sk-proj-...` to `.env`
3. Restart the server

### Error: "Invalid API key"
**Solution:**
1. Verify key format: starts with `sk-proj-`
2. Check key is not expired or revoked at https://platform.openai.com/api-keys
3. Ensure no extra spaces in `.env`: `OPENAI_API_KEY=sk-proj-xxx` (not `OPENAI_API_KEY = sk-proj-xxx`)

### Error: "Model not found"
**Solution:**
1. Verify model name is correct
2. Check if model is available in your OpenAI account region
3. Use default models if unsure

### ChromaDB: "Permission denied" on CHROMA_PATH
**Solution:**
1. Check directory permissions: `chmod 755 ./chroma`
2. Use absolute path with proper permissions
3. Ensure sufficient disk space

---

## Configuration Validation Checklist

Before deploying:
- [ ] `.env` file created with `OPENAI_API_KEY`
- [ ] `.env` NOT committed to git
- [ ] `.env.example` created with template
- [ ] All required variables set
- [ ] Models exist in OpenAI account
- [ ] CHROMA_PATH directory exists or is writable
- [ ] No trailing spaces in variable values
- [ ] Test connection with health check: `curl http://localhost:8000/health`
