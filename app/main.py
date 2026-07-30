from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.services.ingest import ingest_file
from app.services.rag import answer_question

app = FastAPI(
    title="FastAPI RAG Project",
    version="0.1.0",
)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    k: int = Field(default=4, ge=1, le=10)


@app.get("/")
def root():
    return {
        "message": "FastAPI RAG project is running.",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()

        result = ingest_file(
            filename=file.filename,
            file_bytes=file_bytes,
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask")
def ask(payload: AskRequest):
    try:
        return answer_question(
            question=payload.question,
            k=payload.k,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))