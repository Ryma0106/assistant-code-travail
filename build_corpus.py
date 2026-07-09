# build_corpus.py — Construit le corpus JSON depuis l'API Légifrance
# Usage : python build_corpus.py

import json
import os
import time
from datetime import date

from legifrance_client import LegifranceClient
from recuperation_articles import recuperer_article
from constants import THEMES, CORPUS_PATH


def generer_numeros(debut, fin):
    """Génère la liste des numéros d'articles entre deux bornes
    AU SEIN D'UNE MÊME SECTION (préfixe constant).
    Ex : ('L3121-1', 'L3121-36') -> L3121-1, L3121-2, ..., L3121-36"""
    prefixe, num_debut = debut.rsplit("-", 1)
    _, num_fin = fin.rsplit("-", 1)
    return [f"{prefixe}-{i}" for i in range(int(num_debut), int(num_fin) + 1)]


def construire_corpus():
    client = LegifranceClient()
    corpus = []
    aujourd_hui = date.today().isoformat()

    # Chaque thème contient PLUSIEURS plages (la numérotation du Code
    # change de préfixe par section : L1231-x, L1232-x, ...)
    for theme, plages in THEMES.items():
        print(f"\n📚 Thème : {theme}")

        for debut, fin in plages:
            print(f"   Plage {debut} → {fin}")
            numeros = generer_numeros(debut, fin)

            for numero in numeros:
                try:
                    article = recuperer_article(client, numero)
                except Exception as e:
                    print(f"   ⚠️ {numero} : erreur ({e}) — on continue")
                    continue

                if article is None or not article["texte"].strip():
                    print(f"   ⏭️ {numero} : introuvable ou vide — ignoré")
                    continue

                corpus.append({
                    "id": article["id"],
                    "numero_article": article["numero_article"],
                    "titre_section": theme,
                    "texte": article["texte"].strip(),
                    "source": "Code du travail (API Légifrance)",
                    "date_recuperation": aujourd_hui,
                })
                print(f"   ✅ {numero}")

                # Politesse envers l'API : pause entre les requêtes
                time.sleep(0.5)

    # Sauvegarde du corpus
    os.makedirs(os.path.dirname(CORPUS_PATH), exist_ok=True)
    with open(CORPUS_PATH, "w", encoding="utf-8") as f:
        json.dump(corpus, f, ensure_ascii=False, indent=2)

    print(f"\n🎉 Corpus construit : {len(corpus)} articles → {CORPUS_PATH}")


if __name__ == "__main__":
    construire_corpus()