"""
Évaluation du retrieval — Jalon 3
AVANT tout appel au LLM : pour 5 questions dont on connaît l'article attendu,
on vérifie que cet article remonte dans le top-k.
Si ce n'est pas le cas → le problème est dans le chunking, l'embedding ou
le corpus — PAS dans le LLM (qui n'est pas encore branché).
"""

import chromadb
from sentence_transformers import SentenceTransformer

from questions_evaluation import QUESTIONS_TEST

# On réutilise la configuration du jalon 2 (indexation.py)
from indexation import CHEMIN_BASE, NOM_COLLECTION, NOM_MODELE_EMBEDDING

TOP_K = 5  # l'article attendu doit être dans les 5 premiers résultats


def evaluer_retrieval():
    # Chargement de la base persistée et du MÊME modèle qu'à l'indexation
    client = chromadb.PersistentClient(path=CHEMIN_BASE)
    collection = client.get_collection(name=NOM_COLLECTION)
    modele = SentenceTransformer(NOM_MODELE_EMBEDDING)

    print(f"Base chargée : {collection.count()} documents — top-k = {TOP_K}\n")

    nb_reussites = 0

    for cas in QUESTIONS_TEST:
        question = cas["question"]
        attendu = cas["article_attendu"]

        # Encodage de la question et recherche des k plus proches
        vecteur = modele.encode([question]).tolist()
        resultats = collection.query(
            query_embeddings=vecteur,
            n_results=TOP_K,
            include=["metadatas", "distances"],
        )

        # Les numéros d'articles remontés, dans l'ordre
        numeros = [m["numero_article"] for m in resultats["metadatas"][0]]

        if attendu in numeros:
            rang = numeros.index(attendu) + 1
            nb_reussites += 1
            print(f"✅ {question}")
            print(f"   → {attendu} trouvé au rang {rang}/{TOP_K} | top : {numeros}\n")
        else:
            print(f"❌ {question}")
            print(f"   → {attendu} ABSENT du top-{TOP_K} | remontés : {numeros}\n")

    print("=" * 60)
    print(f"BILAN : {nb_reussites}/{len(QUESTIONS_TEST)} articles attendus dans le top-{TOP_K}")


if __name__ == "__main__":
    evaluer_retrieval()