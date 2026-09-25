#!/usr/bin/env bash
# Compare deux stratégies de découpage sur le même jeu de questions.
set -e
for taille in 600 1200; do
  echo "== découpage max_chars=$taille =="
  python -c "from src.rag.ingest import build_index; print(build_index(max_chars=$taille), 'passages')"
  python -m src.rag.evaluate --questions data/eval/questions.jsonl --k 5
done
