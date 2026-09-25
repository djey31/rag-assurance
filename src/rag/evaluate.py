from __future__ import annotations
"""Évaluation du pipeline RAG.

Deux familles de métriques :
  - récupération : recall@k et MRR, calculés automatiquement en vérifiant si
    le passage attendu se trouve parmi les passages récupérés ;
  - génération : taux de citation et taux d'abstention, plus une vérification
    manuelle des hallucinations sur un échantillon (voir le README).
"""
import json, argparse, re
from pathlib import Path
from .retrieve import retrieve
from .answer import answer

def normaliser(t: str) -> str:
    return re.sub(r"\s+", " ", t.lower()).strip()

def passage_trouve(attendu: str, passages: list[dict]) -> int | None:
    a = normaliser(attendu)[:120]
    for i, p in enumerate(passages):
        if a in normaliser(p["text"]):
            return i + 1
    return None

def evaluer(chemin: str, k: int, avec_generation: bool) -> dict:
    lignes = [json.loads(l) for l in Path(chemin).read_text(encoding="utf-8").splitlines() if l.strip()]
    rangs, cite, abstient = [], 0, 0
    for ex in lignes:
        passages = retrieve(ex["question"], k)
        rangs.append(passage_trouve(ex["passage_attendu"], passages))
        if avec_generation:
            rep = answer(ex["question"], k)["reponse"]
            if re.search(r"\[\d+\]", rep):
                cite += 1
            if "je ne trouve pas la réponse" in rep.lower():
                abstient += 1
    n = len(lignes)
    trouves = [r for r in rangs if r]
    resultats = {
        "n_questions": n,
        f"recall@{k}": round(len(trouves) / n, 3) if n else 0.0,
        "mrr": round(sum(1 / r for r in trouves) / n, 3) if n else 0.0,
    }
    if avec_generation:
        resultats["taux_citation"] = round(cite / n, 3)
        resultats["taux_abstention"] = round(abstient / n, 3)
    return resultats

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--questions", default="data/eval/questions.jsonl")
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--generation", action="store_true")
    a = ap.parse_args()
    print(json.dumps(evaluer(a.questions, a.k, a.generation), indent=2, ensure_ascii=False))
