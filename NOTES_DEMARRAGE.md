# Par quoi commencer

## Soirée 1 : les données et l'index
1. `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
2. Télécharger 10 à 15 conditions générales publiques (PDF) dans `data/pdf/`
   Chercher "conditions générales assurance habitation PDF" ou "auto", sur les
   sites des assureurs. Prendre des documents variés (habitation, auto, santé).
3. `cp .env.example .env`, installer Ollama, puis `ollama pull mistral:7b-instruct`
4. `python -m src.rag.ingest` et vérifier le nombre de passages indexés

## Soirée 2 : questions et réponses
1. `uvicorn src.rag.api:app --reload`
2. Tester une dizaine de questions et lire les passages récupérés, pas seulement
   les réponses. C'est là qu'on voit si le découpage est bon.
3. Ajuster le prompt dans `src/rag/answer.py` si le modèle cite mal

## Soirée 3 : le jeu d'évaluation
1. Écrire 30 à 50 questions dans `data/eval/questions.jsonl`, en copiant pour
   chacune le passage exact du PDF qui contient la réponse
2. `python -m src.rag.evaluate --questions data/eval/questions.jsonl --k 5`
3. Noter les résultats dans le tableau du README

## Soirée 4 : amélioration mesurée et mise au propre
1. `bash scripts/comparer_configs.sh` pour comparer deux découpages
2. Compléter le tableau du README avec les deux configurations
3. Pousser sur GitHub, vérifier que le workflow de tests passe
4. Relire le README : question posée, méthode, résultats, limites

## Ensuite, si tu veux aller plus loin
- Ajouter un reranking et mesurer le gain
- Frontend Next.js déployé sur Vercel, l'API restant sur ton VPS
- Comparer un modèle local et une API dans le tableau de résultats
