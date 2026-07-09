# questions_evaluation.py — Jeu d'évaluation du retrieval (jalon 3)
# Pour chaque question : l'article qui DOIT remonter dans le top-k

QUESTIONS_TEST = [
    {
        "question": "Quelle est la durée légale de travail hebdomadaire ?",
        "article_attendu": "L3121-27",   # les fameuses 35 heures
    },
    {
        "question": "Combien de jours de congés payés par mois de travail ?",
        "article_attendu": "L3141-3",    # 2,5 jours ouvrables par mois
    },
    {
        "question": "Qu'est-ce que le harcèlement moral ?",
        "article_attendu": "L1152-1",    # définition du harcèlement moral
    },
    {
        "question": "Comment fonctionne la rupture conventionnelle ?",
        "article_attendu": "L1237-11",   # principe de la rupture conventionnelle
    },
    {
        "question": "Le salarié a-t-il droit à un préavis en cas de licenciement ?",
        "article_attendu": "L1234-1",    # préavis de licenciement
    },
]