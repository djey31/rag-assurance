from __future__ import annotations
"""Génération de la réponse avec citation obligatoire des sources."""
from .retrieve import retrieve
from .llm import generate

PROMPT = """Tu réponds à des questions sur des conditions générales d'assurance.

Règles strictes :
1. Réponds uniquement à partir des passages fournis.
2. Si les passages ne contiennent pas la réponse, écris exactement : "Je ne trouve pas la réponse dans les documents fournis."
3. Cite les passages utilisés en indiquant leur numéro entre crochets, par exemple [2].
4. Ne fais aucune supposition sur ce qui n'est pas écrit.

Passages :
{contexte}

Question : {question}

Réponse :"""

def answer(question: str, k: int | None = None) -> dict:
    passages = retrieve(question, k)
    contexte = "\n\n".join(
        f"[{i+1}] (document {p['doc_id']}, page {p['page']})\n{p['text']}"
        for i, p in enumerate(passages)
    )
    texte = generate(PROMPT.format(contexte=contexte, question=question))
    return {"question": question, "reponse": texte.strip(), "sources": passages}
