from __future__ import annotations
"""Récupération des passages pertinents."""
import chromadb
from sentence_transformers import SentenceTransformer
from .config import settings

_model = None
def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)
    return _model

def retrieve(question, k=None):
    k = k or settings.top_k
    emb = _get_model().encode([f"query: {question}"], normalize_embeddings=True).tolist()
    col = chromadb.PersistentClient(path=settings.chroma_dir).get_collection("cg_assurance")
    res = col.query(query_embeddings=emb, n_results=k)
    return [
        {"chunk_id": cid, "text": doc, "doc_id": meta["doc_id"], "page": meta["page"],
         "distance": dist}
        for cid, doc, meta, dist in zip(res["ids"][0], res["documents"][0],
                                        res["metadatas"][0], res["distances"][0])
    ]
