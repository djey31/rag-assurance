"""Contrôle qualité de l'index : volume par document, taille des passages,
extraits au hasard et test de recherche.

Usage :  python scripts/inspecter_index.py
"""
import random
import statistics as stats
from collections import Counter

import chromadb

from src.rag.config import settings

COLLECTION = "cg_assurance"


def charger():
    client = chromadb.PersistentClient(path=settings.chroma_dir)
    col = client.get_collection(COLLECTION)
    data = col.get(include=["documents", "metadatas"])
    return col, data


def volume_par_document(data):
    print("\n=== 1. NOMBRE DE PASSAGES PAR DOCUMENT ===")
    compte = Counter(m["doc_id"] for m in data["metadatas"])
    tailles = {}
    for doc, meta in zip(data["documents"], data["metadatas"]):
        tailles.setdefault(meta["doc_id"], []).append(len(doc))
    for doc, n in compte.most_common():
        moy = int(stats.mean(tailles[doc]))
        maxi = max(tailles[doc])
        alerte = "  <-- A VERIFIER" if n < 10 or maxi > 3000 else ""
        print(f"{doc:40s} {n:4d} passages | taille moy {moy:5d} | max {maxi:5d}{alerte}")
    print(f"\nTotal : {len(data['documents'])} passages, {len(compte)} documents")


def stats_tailles(data):
    print("\n=== 2. TAILLE DES PASSAGES (caracteres) ===")
    L = sorted(len(d) for d in data["documents"])
    n = len(L)
    def pct(p):
        return L[min(n - 1, int(n * p))]
    print(f"min {L[0]} | p25 {pct(.25)} | mediane {pct(.5)} | p75 {pct(.75)} | p90 {pct(.9)} | max {L[-1]}")
    trop_courts = sum(1 for x in L if x < 200)
    trop_longs = sum(1 for x in L if x > 2000)
    print(f"passages < 200 car. : {trop_courts} ({100*trop_courts/n:.1f} %)")
    print(f"passages > 2000 car. : {trop_longs} ({100*trop_longs/n:.1f} %)")


def extraits(data, k=3):
    print("\n=== 3. EXTRAITS AU HASARD ===")
    idx = random.sample(range(len(data["documents"])), min(k, len(data["documents"])))
    for i in idx:
        m = data["metadatas"][i]
        texte = data["documents"][i].replace("\n", " ")
        print(f"\n--- {m['doc_id']} (page {m['page']}, {len(data['documents'][i])} car.) ---")
        print(texte[:400] + ("..." if len(texte) > 400 else ""))


def test_recherche(questions):
    print("\n=== 4. TEST DE RECHERCHE ===")
    from src.rag.retrieve import retrieve
    for q in questions:
        print(f"\nQuestion : {q}")
        for r in retrieve(q, k=3):
            extrait = r["text"].replace("\n", " ")[:160]
            print(f"  [{r['distance']:.3f}] {r['doc_id']} p.{r['page']} : {extrait}...")


if __name__ == "__main__":
    col, data = charger()
    volume_par_document(data)
    stats_tailles(data)
    extraits(data)
    test_recherche([
        "Quel est le delai de carence ?",
        "Que se passe-t-il en cas de vol du vehicule ?",
        "Quelles sont les exclusions de garantie ?",
    ])
