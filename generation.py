"""
Script de génération avec citations — Jalon 4
Assemble le contexte (chunks pertinents) + le prompt système, 
puis appelle l'API Groq pour générer une réponse citant les articles.
"""

import os
from dotenv import load_dotenv
from groq import Groq
from recherche import rechercher_chunks_pertinents

load_dotenv()

client_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

MODELE_LLM = "llama-3.3-70b-versatile"
TEMPERATURE = 0.2
TOP_K_CHUNKS = 5

AVERTISSEMENT_JURIDIQUE = (
    "Cet assistant ne fournit pas de conseil juridique. "
    "Consultez un avocat ou l'inspection du travail pour votre situation personnelle."
)

PROMPT_SYSTEME = """Tu es un assistant juridique spécialisé dans le droit du travail français.

Tu réponds aux questions UNIQUEMENT à partir des articles de loi fournis dans le contexte ci-dessous.

RÈGLES STRICTES :
1. N'utilise QUE les informations présentes dans le contexte fourni. N'invente JAMAIS un article ou une information qui n'y figure pas.
2. Chaque affirmation de ta réponse doit être suivie du numéro de l'article correspondant, entre parenthèses. Exemple : "La durée légale du travail est de 35 heures par semaine (article L3121-27)."
3. Si le contexte fourni ne permet PAS de répondre à la question, réponds explicitement : "Je ne trouve pas cette information dans ma base de connaissances." Ne tente pas de deviner ou de généraliser à partir de connaissances externes.
4. Si la question demande une interprétation d'une situation personnelle (ex : "mon licenciement est-il abusif ?"), présente le cadre légal général avec ses articles, mais précise clairement que la qualification de la situation nécessite une analyse individualisée par un professionnel.
5. Ne termine pas toi-même par une formule de conseil juridique : elle sera ajoutée automatiquement après ta réponse.

Réponds de façon claire, concise et directement utile."""


def construire_contexte(chunks):
    """Formate les chunks retrouvés en un contexte numéroté pour le LLM."""
    lignes = []
    for i, chunk in enumerate(chunks, start=1):
        lignes.append(
            f"[Source {i}] Article {chunk['numero_article']} "
            f"({chunk['section_thematique']}) : {chunk['texte']}"
        )
    return "\n\n".join(lignes)


def generer_reponse(question, top_k=TOP_K_CHUNKS):
    """
    Pipeline complet : recherche des chunks pertinents, construction du prompt,
    appel au LLM, et ajout systématique de l'avertissement juridique.
    """
    chunks = rechercher_chunks_pertinents(question, top_k=top_k)
    contexte = construire_contexte(chunks)

    messages = [
        {"role": "system", "content": PROMPT_SYSTEME},
        {
            "role": "user",
            "content": f"Contexte (articles du Code du travail) :\n\n{contexte}\n\nQuestion : {question}",
        },
    ]

    reponse = client_groq.chat.completions.create(
        model=MODELE_LLM,
        messages=messages,
        temperature=TEMPERATURE,
    )

    texte_reponse = reponse.choices[0].message.content.strip()

    # Verrou en code : l'avertissement est TOUJOURS ajouté, indépendamment de ce que fait le LLM
    reponse_finale = f"{texte_reponse}\n\n{AVERTISSEMENT_JURIDIQUE}"

    return {
        "reponse": reponse_finale,
        "articles_sources": [c["numero_article"] for c in chunks],
    }


if __name__ == "__main__":
    questions_a_tester = [
        "Combien de jours de congés payés par mois de travail ?",
        "Qu'est-ce que le harcèlement moral au travail ?",
        "Quel est le délai de préavis en cas de licenciement ?",
    ]

    for question_test in questions_a_tester:
        resultat = generer_reponse(question_test)
        print(f"Question : {question_test}\n")
        print(f"Réponse :\n{resultat['reponse']}\n")
        print(f"Articles sources utilisés : {resultat['articles_sources']}")
        print("=" * 70)