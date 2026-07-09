# test_un_article.py — Récupère UN article pour valider le mécanisme

from legifrance_client import LegifranceClient
from recuperation_articles import recuperer_article

client = LegifranceClient()

# L3121-27 : la durée légale de 35h — un grand classique pour tester !
article = recuperer_article(client, "L3121-27")

if article is None:
    print("❌ Article introuvable")
else:
    print(f"✅ Article {article['numero_article']} récupéré !")
    print(f"ID interne : {article['id']}")
    print(f"Texte : {article['texte'][:300]}")