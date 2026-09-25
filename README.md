# Assistant conditions générales d'assurance (RAG)

Un système de question-réponse sur des conditions générales d'assurance
(auto, santé, prévoyance). Il répond en s'appuyant **uniquement** sur les
documents indexés, **cite ses sources** (document et page), et **s'abstient**
quand l'information n'est pas dans les contrats plutôt que d'inventer.

**Démo en ligne :** https://rag-assurance-l84lyjj4nxvuvum9tmxcr5.streamlit.app

---

## Aperçu

- 15 contrats indexés (auto, santé, prévoyance), 2 343 passages
- Recherche sémantique multilingue, réponses sourcées, garde-fou d'abstention
- Architecture modulaire : le modèle de génération se change via une variable
  d'environnement (Ollama en local, Groq ou Anthropic en ligne)

## Comment ça marche

Le pipeline se décompose en quatre étapes.

1. **Extraction** (`ingest.py`) : lecture des PDF page par page avec pdfplumber,
   en conservant le numéro de page pour la citation.
2. **Découpage** (`chunking.py`) : découpage par paragraphes puis par phrases,
   avec recouvrement, en garantissant que chaque passage reste sous la limite
   du modèle d'embeddings (512 tokens). Ce contrôle évite la troncature
   silencieuse d'une partie du texte à l'indexation.
3. **Vectorisation et indexation** : chaque passage est encodé avec
   `intfloat/multilingual-e5-base` (préfixes `passage:` / `query:`, vecteurs
   normalisés) puis stocké dans ChromaDB avec son texte et ses métadonnées.
4. **Génération** (`answer.py`) : la question est vectorisée, les passages les
   plus proches sont récupérés, puis transmis au modèle avec une consigne
   stricte : répondre uniquement à partir des passages, citer les numéros
   utilisés, et écrire « Je ne trouve pas la réponse dans les documents
   fournis » sinon.

## Choix techniques

- **Découpage sous la limite du modèle** : un passage trop long est tronqué
  côté embeddings sans erreur visible. Le découpage garantit des passages
  courts et complets, condition d'une recherche fiable.
- **Embeddings multilingues E5** : adaptés au français juridique, avec la
  convention de préfixes `passage:` / `query:`.
- **Abstention** : le prompt impose de dire « Je ne trouve pas » en l'absence
  d'information, ce qui limite les hallucinations sur des documents contractuels.
- **Couche LLM agnostique** (`llm.py`) : Ollama, Groq (OpenAI-compatible) ou
  Anthropic, sélectionnés par variable d'environnement, sans changer le reste
  du code.

## Évaluation

Le module `evaluate.py` mesure la qualité de la recherche et de la génération
sur un jeu de questions annotées : recall@k, MRR, taux de citation et taux
d'abstention. Le script `scripts/comparer_configs.sh` compare plusieurs
configurations (taille des passages, valeur de k).

## Lancer en local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Placer des PDF dans `data/pdf/`, puis indexer :

```bash
python -m src.rag.ingest
```

Configurer le modèle de génération dans un fichier `.env`
(voir `.env.example`), puis lancer l'interface :

```bash
streamlit run streamlit_app.py
```

## Stack technique

Python · pdfplumber · sentence-transformers (E5) · ChromaDB · Groq /
Ollama / Anthropic · FastAPI · Streamlit · pytest · GitHub Actions

## Limites connues

- L'index est figé : ajouter un contrat demande une réindexation.
- Un passage à cheval sur deux pages est rattaché à la première.
- Les documents scannés (sans texte sélectionnable) ne sont pas gérés
  (OCR non intégré).

---

Projet personnel · Djénéba Coulibaly ·
[Portfolio](https://djey31.github.io)
