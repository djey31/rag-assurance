from __future__ import annotations
"""Découpage des documents en passages.

Objectif : des passages qui tiennent sous la limite du modèle d'embeddings
(512 tokens pour E5, soit environ 1800 caractères en francais). Au-dela,
le texte est tronque silencieusement et n'est jamais indexe.

Strategie, du plus fin au plus grossier :
1. decoupage par paragraphes quand le PDF en fournit (lignes vides) ;
2. si un paragraphe depasse la taille cible, on le recoupe par phrases ;
3. si une phrase depasse encore, on coupe brutalement a la taille cible.
Un recouvrement conserve la fin du passage precedent pour ne pas perdre
une information a cheval sur deux passages.
"""
from dataclasses import dataclass
import re

@dataclass
class Chunk:
    doc_id: str
    chunk_id: str
    text: str
    page: int


def split_paragraphs(text):
    """Coupe sur les lignes vides, puis sur les simples sauts de ligne
    si le PDF n'a pas produit de lignes vides."""
    parts = re.split(r"\n\s*\n", text)
    parts = [p.strip() for p in parts if p.strip()]
    return parts


def split_sentences(text):
    """Coupe apres un point, un point-virgule ou deux-points suivis d'un espace.
    Rudimentaire mais suffisant pour du texte contractuel."""
    parts = re.split(r"(?<=[.;:])\s+", text)
    return [p.strip() for p in parts if p.strip()]


def decouper_morceau(texte, taille_max):
    """Garantit qu'aucun fragment ne depasse taille_max."""
    if len(texte) <= taille_max:
        return [texte]
    fragments, courant = [], ""
    for phrase in split_sentences(texte):
        # une phrase seule trop longue : coupe brutale
        while len(phrase) > taille_max:
            if courant:
                fragments.append(courant)
                courant = ""
            fragments.append(phrase[:taille_max])
            phrase = phrase[taille_max:]
        if len(courant) + len(phrase) + 1 <= taille_max:
            courant = (courant + " " + phrase).strip()
        else:
            if courant:
                fragments.append(courant)
            courant = phrase
    if courant:
        fragments.append(courant)
    return fragments


def chunk_text(doc_id, pages, max_chars=1000, overlap=150):
    """pages : liste de (numero_de_page, texte).
    Retourne une liste de Chunk dont aucun ne depasse max_chars."""
    chunks = []
    buffer, buf_page = "", None

    def flush():
        nonlocal buffer, buf_page
        if buffer.strip():
            chunks.append(Chunk(doc_id, f"{doc_id}-{len(chunks)}",
                                buffer.strip(), buf_page or 1))
        buffer = ""

    for page_no, page_text in pages:
        if not page_text:
            continue
        for para in split_paragraphs(page_text):
            for frag in decouper_morceau(para, max_chars):
                if buf_page is None:
                    buf_page = page_no
                if len(buffer) + len(frag) + 1 <= max_chars:
                    buffer = (buffer + "\n" + frag).strip()
                else:
                    queue = buffer[-overlap:] if overlap else ""
                    flush()
                    buf_page = page_no
                    buffer = (queue + "\n" + frag).strip()
                    # securite : si le recouvrement fait deborder, on coupe
                    if len(buffer) > max_chars:
                        buffer = buffer[-max_chars:]
    flush()
    return chunks