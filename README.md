# Assistant RAG sur conditions générales d'assurance

Un assistant qui répond à des questions sur des conditions générales d'assurance
en citant systématiquement ses sources, avec une **évaluation chiffrée** de la
qualité des réponses.

Le point central du projet n'est pas le pipeline RAG, qui est standard, mais la
mesure : savoir si le système trouve réellement la bonne information, et à quel
prix.

## Résultats

| Configuration | recall@5 | MRR | Taux de citation | Taux d'abstention |
|---|---|---|---|---|
| Découpage 600 caractères, Mistral 7B local | à compléter | | | |
| Découpage 1200 caractères par paragraphe, Mistral 7B local | | | | |
| Découpage 1200 caractères, modèle via API | | | | |

Lecture : à compléter après la première campagne d'évaluation.

## Architecture

```
PDF → extraction (pdfplumber) → découpage par paragraphe
    → embeddings multilingues (e5-base) → ChromaDB
                                            ↓
question → embedding → récupération top-k → prompt contraint → réponse + sources
```

Le fournisseur de génération est abstrait dans `src/rag/llm.py` : Ollama en
local, API Anthropic, ou toute API compatible OpenAI. Cela permet de comparer un
modèle ouvert et un modèle propriétaire sur les mêmes questions, en ne changeant
qu'une variable d'environnement.

## Installation

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Pour le modèle en local :

```bash
ollama pull mistral:7b-instruct
```

## Utilisation

```bash
# 1. Déposer des PDF dans data/pdf/ puis indexer
python -m src.rag.ingest

# 2. Lancer l'API
uvicorn src.rag.api:app --reload

# 3. Évaluer
python -m src.rag.evaluate --questions data/eval/questions.jsonl --k 5 --generation
```

## Évaluation

Le jeu d'évaluation (`data/eval/questions.jsonl`) associe à chaque question le
passage du document qui contient la réponse. Voir `questions.example.jsonl` pour
le format.

- **recall@k** : le bon passage figure-t-il parmi les k passages récupérés
- **MRR** : à quelle position il apparaît
- **taux de citation** : la réponse cite-t-elle au moins une source
- **taux d'abstention** : le système reconnaît-il qu'il ne sait pas

Le taux d'hallucination est vérifié à la main sur un échantillon, car il ne se
mesure pas automatiquement de façon fiable.

## Limites connues

- Jeu d'évaluation construit manuellement, donc de taille réduite
- L'extraction des tableaux dans les PDF reste imparfaite
- Pas de reranking pour l'instant, c'est la prochaine amélioration à mesurer

## Licence

MIT
