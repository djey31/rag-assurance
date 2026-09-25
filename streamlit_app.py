"""Interface Streamlit du RAG assurance.

N'ajoute qu'une page web au pipeline existant (retrieve + answer).
Les cles (Groq) sont lues depuis les secrets Streamlit, qui sont aussi
exposes comme variables d'environnement et donc repris par la config.
"""
import streamlit as st

from src.rag.answer import answer

st.set_page_config(page_title="RAG Assurance", page_icon="📄")

st.title("Assistant conditions générales d'assurance")
st.caption(
    "Pose une question sur un ensemble de contrats (auto, santé, prévoyance). "
    "La réponse est fondée uniquement sur les documents indexés, avec citation "
    "des passages sources. Le système répond \"Je ne trouve pas\" quand "
    "l'information n'y figure pas."
)

EXEMPLES = [
    "Que se passe-t-il en cas de vol du véhicule ?",
    "Quel est le délai de carence en prévoyance ?",
    "Quelles sont les exclusions de garantie ?",
]

with st.sidebar:
    st.subheader("Exemples")
    for ex in EXEMPLES:
        if st.button(ex):
            st.session_state["question"] = ex

question = st.text_input(
    "Votre question",
    key="question",
    placeholder="Ex : que se passe-t-il en cas de vol ?",
)

if st.button("Rechercher", type="primary") or question:
    if question and question.strip():
        with st.spinner("Recherche dans les contrats..."):
            res = answer(question)
        st.markdown("### Réponse")
        st.markdown(res["reponse"])
        with st.expander("Passages sources utilisés"):
            for i, p in enumerate(res["sources"], start=1):
                extrait = p["text"].replace("\n", " ").strip()
                if len(extrait) > 350:
                    extrait = extrait[:350] + "..."
                st.markdown(f"**[{i}] {p['doc_id']} — page {p['page']}**")
                st.write(extrait)
                st.divider()
