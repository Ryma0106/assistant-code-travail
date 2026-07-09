"""
Script d'indexation — Jalon 2
Construit (ou recharge) la base vectorielle ChromaDB à partir du corpus.
Gère la persistance ET la détection de changement du corpus (fraîcheur).
"""

import hashlib
import json
import os
import chromadb
from sentence_transformers import SentenceTransformer
from donnees_test import corpus_test  # à remplacer plus tard par le vrai corpus de Ryma

# --- Configuration ---
NOM_MODELE_EMBEDDING = "paraphrase-multilingual-MiniLM-L12-v2"
CHEMIN_BASE = "./chroma_db"
FICHIER_METADATA = "./index_metadata.json"
NOM_COLLECTION = "code_du_travail"


def calculer_hash_corpus(corpus):
    """
    Calcule une empreinte unique du corpus.
    Si le contenu change (même un seul caractère), le hash change.
    Ça nous permet de savoir si on doit réindexer ou non.
    """
    contenu_complet = "".join(doc["texte"] + doc["numero_article"] for doc in corpus)
    return hashlib.sha256(contenu_complet.encode("utf-8")).hexdigest()


def charger_metadata_existante():
    """Lit le fichier de métadonnées d'indexation s'il existe, sinon retourne None."""
    if os.path.exists(FICHIER_METADATA):
        with open(FICHIER_METADATA, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def sauvegarder_metadata(hash_corpus):
    """Sauvegarde le hash du corpus et le nom du modèle utilisé."""
    metadata = {
        "hash_corpus": hash_corpus,
        "modele_embedding": NOM_MODELE_EMBEDDING,
        "nombre_documents": len(corpus_test),
    }
    with open(FICHIER_METADATA, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)


def preparer_chunks(corpus):
    """
    Stratégie de chunking : un article = un chunk.
    Le texte embeddé est préfixé par la section thématique (approche hybride, Q1).
    """
    chunks = []
    for doc in corpus:
        texte_enrichi = f"{doc['section_thematique']} — Article {doc['numero_article']} : {doc['texte']}"
        chunks.append({
            "id": doc["id"],
            "texte_embedde": texte_enrichi,
            "numero_article": doc["numero_article"],
            "section_thematique": doc["section_thematique"],
            "source": doc["source"],
        })
    return chunks


def construire_index():
    hash_actuel = calculer_hash_corpus(corpus_test)
    metadata_existante = charger_metadata_existante()

    client = chromadb.PersistentClient(path=CHEMIN_BASE)

    # Cas 1 : la base existe déjà ET le corpus n'a pas changé → on recharge, pas de réindexation
    if metadata_existante and metadata_existante["hash_corpus"] == hash_actuel:
        print("Corpus inchangé. Chargement de la base existante, pas de réindexation.")
        collection = client.get_collection(name=NOM_COLLECTION)
        print(f"Base chargée : {collection.count()} documents.")
        return collection

    # Cas 2 : premier lancement OU corpus modifié → on (ré)indexe
    if metadata_existante:
        print("Le corpus a changé depuis la dernière indexation. Réindexation en cours...")
        client.delete_collection(name=NOM_COLLECTION)
    else:
        print("Aucune base existante. Première indexation...")

    chunks = preparer_chunks(corpus_test)

    print(f"Chargement du modèle d'embedding : {NOM_MODELE_EMBEDDING}...")
    modele = SentenceTransformer(NOM_MODELE_EMBEDDING)

    textes = [c["texte_embedde"] for c in chunks]
    print("Encodage des chunks en vecteurs...")
    embeddings = modele.encode(textes).tolist()

    collection = client.create_collection(name=NOM_COLLECTION)
    collection.add(
        ids=[c["id"] for c in chunks],
        documents=textes,
        embeddings=embeddings,
        metadatas=[
            {
                "numero_article": c["numero_article"],
                "section_thematique": c["section_thematique"],
                "source": c["source"],
            }
            for c in chunks
        ],
    )

    sauvegarder_metadata(hash_actuel)
    print(f"Indexation terminée : {collection.count()} documents indexés.")
    return collection


if __name__ == "__main__":
    collection = construire_index()

    # Contrôle qualité : afficher quelques chunks avec leurs métadonnées
    print("\n--- Contrôle qualité : aperçu des chunks indexés ---")
    resultat = collection.get(limit=3, include=["documents", "metadatas"])
    for doc, meta in zip(resultat["documents"], resultat["metadatas"]):
        print(f"\nArticle {meta['numero_article']} ({meta['section_thematique']})")
        print(f"Texte : {doc}")