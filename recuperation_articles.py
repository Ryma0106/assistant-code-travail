# recuperation_articles.py — Recherche et récupération d'articles du Code du travail

import time


def chercher_id_article(client, numero_article):
    """Cherche l'identifiant interne (LEGIARTI...) d'un article
    à partir de son numéro (ex : 'L3121-27')."""
    payload = {
        "recherche": {
            "champs": [
                {
                    "typeChamp": "NUM_ARTICLE",
                    "criteres": [
                        {
                            "typeRecherche": "EXACTE",
                            "valeur": numero_article,
                            "operateur": "ET",
                        }
                    ],
                    "operateur": "ET",
                }
            ],
            "filtres": [
                {"facette": "NOM_CODE", "valeurs": ["Code du travail"]},
                {"facette": "DATE_VERSION", "singleDate": int(time.time() * 1000)},
            ],
            "pageNumber": 1,
            "pageSize": 10,
            "operateur": "ET",
            "typePagination": "ARTICLE",
            "sort": "PERTINENCE",
        },
        "fond": "CODE_DATE",
    }

    resultat = client.post("/search", payload)

    # On fouille la réponse pour trouver l'identifiant LEGIARTI
    try:
        premier = resultat["results"][0]
        extract = premier["sections"][0]["extracts"][0]
        return extract["id"]
    except (KeyError, IndexError):
        return None  # article introuvable


def recuperer_article(client, numero_article):
    """Récupère le texte complet d'un article à partir de son numéro."""
    id_article = chercher_id_article(client, numero_article)
    if id_article is None:
        return None

    resultat = client.post("/consult/getArticle", {"id": id_article})
    article = resultat.get("article", {})

    return {
        "id": id_article,
        "numero_article": article.get("num", numero_article),
        "texte": article.get("texte", ""),
    }