# controle_qualite.py — Affiche 10 articles au hasard pour relecture (exigence du sujet)

import json
import random

from constants import CORPUS_PATH

with open(CORPUS_PATH, encoding="utf-8") as f:
    corpus = json.load(f)

print(f"📊 Corpus : {len(corpus)} articles\n")

# Répartition par thème
themes = {}
for doc in corpus:
    themes[doc["titre_section"]] = themes.get(doc["titre_section"], 0) + 1
for theme, nb in themes.items():
    print(f"   {nb:3d} articles — {theme}")

print("\n" + "=" * 70)
print("RELECTURE DE 10 ARTICLES AU HASARD")
print("=" * 70)

for doc in random.sample(corpus, 10):
    print(f"\n📄 {doc['numero_article']} — {doc['titre_section']}")
    print(doc["texte"][:400])