"""
Interface web — Jalon 6 (amélioration bonus)
Interface graphique Streamlit en complément de la CLI (jalon 5).
Améliorations : scores de pertinence (jalon 6 "score de confiance"),
liens directs vers Légifrance, exemples de questions.
Lancement : streamlit run app_web.py
"""

import json

import streamlit as st

from generation import generer_reponse, AVERTISSEMENT_JURIDIQUE
from recherche import rechercher_chunks_pertinents
from constants import CORPUS_PATH

# ---------------------------------------------------------------
# Configuration de la page + styles
# ---------------------------------------------------------------
st.set_page_config(
    page_title="Assistant Code du travail",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .titre-banniere {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 1.4rem 2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    .titre-banniere h1 { color: white; margin: 0; font-size: 1.9rem; }
    .titre-banniere p { color: #dbeafe; margin: 0.3rem 0 0 0; }

    .badge-article {
        display: inline-block;
        background: #1e3a8a;
        color: white !important;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        margin: 0.15rem;
        font-size: 0.85rem;
        text-decoration: none;
    }
    .badge-article:hover { background: #3b82f6; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------
def lire_infos_corpus():
    try:
        with open(CORPUS_PATH, encoding="utf-8") as f:
            corpus = json.load(f)
        themes = sorted({d["titre_section"] for d in corpus})
        return corpus[0].get("date_recuperation", "date inconnue"), len(corpus), themes
    except (FileNotFoundError, IndexError, json.JSONDecodeError):
        return "date inconnue", 0, []


def lien_legifrance(numero_article):
    """Lien de recherche Légifrance pour vérifier un article à la source."""
    return f"https://www.legifrance.gouv.fr/search/all?query={numero_article}&tab_selection=all"


date_corpus, nb_articles, themes = lire_infos_corpus()

# ---------------------------------------------------------------
# Sidebar : la carte d'identité du système
# ---------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ À propos du système")
    st.metric("Articles indexés", nb_articles)
    st.metric("Corpus à jour au", date_corpus)

    st.markdown("**Thèmes couverts :**")
    for t in themes:
        st.markdown(f"- {t}")

    st.divider()
    st.markdown(
        "**Pipeline :** RAG (retrieval augmenté)\n\n"
        "**Embedding :** paraphrase-multilingual-MiniLM-L12-v2\n\n"
        "**Base vectorielle :** ChromaDB (persistée)\n\n"
        "**LLM :** llama-3.3-70b (Groq), température 0.2"
    )
    st.divider()
    st.caption(
        "⚠️ Le droit évolue. Vérifiez sur legifrance.gouv.fr "
        "que les articles cités sont toujours en vigueur."
    )

# ---------------------------------------------------------------
# Bandeau titre
# ---------------------------------------------------------------
st.markdown("""
<div class="titre-banniere">
    <h1>⚖️ Assistant Code du travail</h1>
    <p>Posez vos questions en langage naturel — chaque réponse cite ses articles.</p>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------
# État de session
# ---------------------------------------------------------------
if "historique" not in st.session_state:
    st.session_state.historique = []
if "question_exemple" not in st.session_state:
    st.session_state.question_exemple = None

# ---------------------------------------------------------------
# Exemples de questions cliquables (affichés tant que pas d'historique)
# ---------------------------------------------------------------
if not st.session_state.historique:
    st.markdown("##### 💡 Essayez par exemple :")
    exemples = [
        "Combien d'heures supplémentaires peut-on faire par semaine ?",
        "Comment fonctionne la rupture conventionnelle ?",
        "Qu'est-ce que le harcèlement moral au travail ?",
    ]
    cols = st.columns(len(exemples))
    for col, ex in zip(cols, exemples):
        if col.button(ex, use_container_width=True):
            st.session_state.question_exemple = ex

# ---------------------------------------------------------------
# LA ZONE DE SAISIE : champ de chat en bas de page
# (+ récupération d'un éventuel exemple cliqué)
# ---------------------------------------------------------------
question = st.chat_input("✍️ Posez votre question sur le droit du travail...")

if st.session_state.question_exemple:
    question = st.session_state.question_exemple
    st.session_state.question_exemple = None

# ---------------------------------------------------------------
# Traitement de la question
# ---------------------------------------------------------------
if question:
    with st.spinner("🔍 Recherche dans le Code du travail..."):
        try:
            resultat = generer_reponse(question)
            # Distances des chunks pour le score de confiance (jalon 6)
            chunks = rechercher_chunks_pertinents(question, top_k=5)
            resultat["chunks_detail"] = chunks
            st.session_state.historique.append((question, resultat))
        except Exception as e:
            st.error(f"Une erreur est survenue : {e}. "
                     "Vérifiez votre connexion et votre clé API.")