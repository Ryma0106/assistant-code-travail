"""
Fonction de recherche — réutilisée par le jalon 4 (génération)
Récupère les chunks les plus pertinents pour une question donnée.
"""

import chromadb
from sentence_transformers import SentenceTransformer
from indexation import NOM_MODELE_EMBEDDING, CHEMIN_BASE, NOM_COLLECTION

# On charge le modèle une seule fois (coûteux à charger, autant le garder en mémoire)
_modele = None
_collection = None


def _obtenir_modele():
    global _modele
    if _modele is None:
        _modele = SentenceTransformer(NOM_MODELE_EMBEDDING)
    return _modele


def _obtenir_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHEMIN_BASE)
        _collection = client.get_collection(name=NOM_COLLECTION)
    return _collection


def rechercher_chunks_pertinents(question, top_k=5):
    """
    Cherche les top_k chunks les plus proches sémantiquement de la question.
    Retourne une liste de dictionnaires : texte, numero_article, section_thematique, score_distance.
    """
    modele = _obtenir_modele()
    collection = _obtenir_collection()

    vecteur_question = modele.encode([question]).tolist()

    resultats = collection.query(
        query_embeddings=vecteur_question,
        n_results=top_k,
    )

    chunks_trouves = []
    for doc, meta, distance in zip(
        resultats["documents"][0],
        resultats["metadatas"][0],
        resultats["distances"][0],
    ):
        chunks_trouves.append({
            "texte": doc,
            "numero_article": meta["numero_article"],
            "section_thematique": meta["section_thematique"],
            "distance": distance,
        })

    return chunks_trouves


if __name__ == "__main__":
    # Petit test manuel rapide
    question_test = "Quelle est la durée légale du travail par semaine ?"
    resultats = rechercher_chunks_pertinents(question_test, top_k=3)

    print(f"Question : {question_test}\n")
    for i, chunk in enumerate(resultats, start=1):
        print(f"[{i}] Article {chunk['numero_article']} ({chunk['section_thematique']}) — distance={chunk['distance']:.4f}")
        print(f"    {chunk['texte'][:150]}...\n")