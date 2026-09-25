"""Interface Streamlit du RAG assurance.

N'ajoute qu'une page web au pipeline existant (retrieve + answer).
Les cles sont lues depuis les secrets Streamlit, exposes aussi comme
variables d'environnement et donc repris par la configuration.
"""
import streamlit as st

from src.rag.answer import answer

st.set_page_config(
    page_title="Assistant contrats d'assurance",
    layout="centered",
)

NAVY = "#1F3864"
BLEU = "#2E5FA3"

st.markdown(
    f"""
    <style>
      .stApp {{ background: #f6f8fc; }}
      .block-container {{ padding-top: 2.2rem; max-width: 820px; }}

      /* En-tete */
      .entete {{
        background: linear-gradient(135deg, {NAVY} 0%, {BLEU} 55%, #4f83d1 100%);
        color: #fff; padding: 30px 32px; border-radius: 18px;
        box-shadow: 0 10px 30px rgba(31,56,100,0.18);
      }}
      .entete h1 {{ color:#fff; margin:0 0 8px 0; font-size:1.7rem; font-weight:700; line-height:1.2; }}
      .entete p {{ color:#dde7fb; margin:0; font-size:0.98rem; line-height:1.5; }}

      /* Puces d'info */
      .puces {{ margin: 16px 0 4px 0; }}
      .puce {{
        display:inline-block; background:#fff; color:{NAVY};
        border:1px solid #dbe3f4; padding:5px 13px; border-radius:999px;
        font-size:0.8rem; font-weight:500; margin:3px 6px 3px 0;
      }}

      /* Boutons */
      .stButton > button {{
        border-radius:10px; border:1px solid #d5deef; background:#fff; color:{NAVY};
        font-weight:500; transition:all .15s ease;
      }}
      .stButton > button:hover {{
        border-color:{BLEU}; color:{BLEU}; background:#f0f5ff;
      }}
      .stButton > button[kind="primary"] {{
        background:{BLEU}; color:#fff; border:none;
      }}
      .stButton > button[kind="primary"]:hover {{ background:{NAVY}; color:#fff; }}

      /* Carte reponse */
      .carte-reponse {{
        background:#fff; border-left:5px solid {BLEU}; border-radius:12px;
        padding:20px 24px; margin-top:6px; box-shadow:0 4px 18px rgba(31,56,100,0.07);
      }}
      .titre-section {{ color:{NAVY}; font-weight:700; font-size:1.05rem; margin:26px 0 8px 0; }}

      /* Sources */
      .src {{
        background:#fff; border:1px solid #e6ebf5; border-radius:12px;
        padding:14px 18px; margin-bottom:12px;
      }}
      .src-titre {{ color:{NAVY}; font-weight:600; font-size:0.92rem; margin-bottom:6px; }}
      .src-texte {{ color:#4b5563; font-size:0.86rem; line-height:1.5; }}
      .src-badge {{
        display:inline-block; padding:2px 10px; border-radius:999px;
        font-size:0.72rem; font-weight:600; margin-left:8px;
      }}
      .pied {{ color:#8a94a6; font-size:0.82rem; text-align:center; margin-top:38px; padding-bottom:20px; }}
      .pied a {{ color:{BLEU}; text-decoration:none; font-weight:500; }}
      header[data-testid="stHeader"] {{ background:transparent; }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="entete">
      <h1>Assistant conditions générales d'assurance</h1>
      <p>Posez une question sur un ensemble de contrats. La réponse est fondée
      uniquement sur les documents indexés et cite ses sources. Le système
      répond « Je ne trouve pas » lorsque l'information n'y figure pas.</p>
    </div>
    <div class="puces">
      <span class="puce">15 contrats</span>
      <span class="puce">Auto · Santé · Prévoyance</span>
      <span class="puce">2 343 passages indexés</span>
      <span class="puce">Recherche sémantique</span>
      <span class="puce">Réponses sourcées</span>
    </div>
    """,
    unsafe_allow_html=True,
)

EXEMPLES = [
    "Que se passe-t-il en cas de vol du véhicule ?",
    "Quelles sont les exclusions de garantie ?",
    "Comment résilier mon contrat ?",
    "Quelles garanties en cas de bris de glace ?",
]
st.markdown('<div class="titre-section">Exemples de questions</div>', unsafe_allow_html=True)
cols = st.columns(2)
for i, ex in enumerate(EXEMPLES):
    if cols[i % 2].button(ex, use_container_width=True):
        st.session_state["question"] = ex

question = st.text_input(
    "Votre question",
    key="question",
    placeholder="Ex : que se passe-t-il en cas de vol ?",
)
lancer = st.button("Rechercher", type="primary", use_container_width=True)


def badge(distance):
    if distance < 0.30:
        return '<span class="src-badge" style="background:#dcfce7;color:#166534;">forte correspondance</span>'
    if distance < 0.40:
        return '<span class="src-badge" style="background:#fef9c3;color:#854d0e;">correspondance moyenne</span>'
    return '<span class="src-badge" style="background:#eef1f6;color:#556070;">correspondance faible</span>'


if (lancer or question) and question and question.strip():
    with st.spinner("Recherche dans les contrats..."):
        res = answer(question)

    st.markdown('<div class="titre-section">Réponse</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="carte-reponse">{res["reponse"]}</div>', unsafe_allow_html=True)

    st.markdown(
        f'<div class="titre-section">Passages sources ({len(res["sources"])})</div>',
        unsafe_allow_html=True,
    )
    for i, p in enumerate(res["sources"], start=1):
        extrait = p["text"].replace("\n", " ").strip()
        if len(extrait) > 360:
            extrait = extrait[:360] + "..."
        st.markdown(
            f'<div class="src"><div class="src-titre">[{i}] {p["doc_id"]} — page {p["page"]}'
            f'{badge(p["distance"])}</div><div class="src-texte">{extrait}</div></div>',
            unsafe_allow_html=True,
        )

st.markdown(
    """
    <div class="pied">
      Projet personnel — RAG sur documents d'assurance · Djénéba Coulibaly ·
      <a href="https://github.com/djey31/rag-assurance" target="_blank">Code source</a> ·
      <a href="https://djey31.github.io" target="_blank">Portfolio</a>
    </div>
    """,
    unsafe_allow_html=True,
)
