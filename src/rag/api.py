from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .answer import answer

app = FastAPI(title="RAG Conditions Générales")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class Question(BaseModel):
    question: str
    k: int | None = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ask")
def ask(q: Question):
    return answer(q.question, q.k)
