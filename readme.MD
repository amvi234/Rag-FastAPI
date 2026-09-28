# RAG Pipeline
This includes Ingestion, Chunking, Embedding and Vector Storage.
Uses Open source LLM models with LangChain.

Uses uv for package management and development:
[UV reference link](https://docs.astral.sh/uv/)

## Run the server
```
uv run fastapi dev app/main.py
```

## Check the Data Flow and Services Details

[SERVICE SPEC](docs/SERVICE_SPEC.md)

## RAG Pipeline Workflow

```mermaid
flowchart TD
    A[📄 Upload Document]
    B[📝 Extract Text]
    C[✂️ Split into Chunks]
    D[🧠 Create Embeddings]
    E[(🗄️ ChromaDB<br/>Store Chunks + Embeddings)]
    F[❓ User Asks Question]
    G[🔍 Embed Question]
    H[📑 Retrieve Similar Chunks]
    I[🤖 Send Retrieved Chunks + Question to LLM]
    J[✅ Return Answer + Sources]

    A --> B
    B --> C
    C --> D
    D --> E
    F --> G
    G --> H
    E --> H
    H --> I
    I --> J
```

## Screenshots
![Ingest Pdf](image.png)
![Ask Question](image-1.png)