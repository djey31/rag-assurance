from __future__ import annotations
"""Extraction des PDF, découpage, indexation dans Chroma."""
from pathlib import Path
import pdfplumber, chromadb
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from .chunking import chunk_text
from .config import settings

def read_pdf(path: Path) -> list[tuple[int, str]]:
    pages = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            pages.append((i, page.extract_text() or ""))
    return pages

def build_index(pdf_dir: str = "data/pdf", max_chars: int = 1200) -> int:
    model = SentenceTransformer(settings.embedding_model)
    client = chromadb.PersistentClient(path=settings.chroma_dir)
    col = client.get_or_create_collection("cg_assurance")
    total = 0
    for pdf in tqdm(sorted(Path(pdf_dir).glob("*.pdf"))):
        chunks = chunk_text(pdf.stem, read_pdf(pdf), max_chars=max_chars)
        if not chunks:
            continue
        embeddings = model.encode([f"passage: {c.text}" for c in chunks],
                                  normalize_embeddings=True).tolist()
        col.upsert(
            ids=[c.chunk_id for c in chunks],
            documents=[c.text for c in chunks],
            embeddings=embeddings,
            metadatas=[{"doc_id": c.doc_id, "page": c.page} for c in chunks],
        )
        total += len(chunks)
    return total

if __name__ == "__main__":
    print(f"{build_index()} passages indexés")
