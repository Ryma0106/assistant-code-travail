# constants.py — Configuration centrale du projet

# --- API Légifrance (PRODUCTION) ---
LEGIFRANCE_TOKEN_URL = "https://oauth.piste.gouv.fr/api/oauth/token"
LEGIFRANCE_API_BASE_URL = "https://api.piste.gouv.fr/dila/legifrance/lf-engine-app"

# --- Corpus ---
CORPUS_PATH = "data/corpus.json"

# --- Les 8 thèmes du sujet ---
# Chaque thème = une liste de plages À PRÉFIXE CONSTANT
# (la numérotation du Code change de préfixe par section : L1231-x, L1232-x...)
THEMES = {
    "Durée du travail et heures supplémentaires": [
        ("L3121-1", "L3121-36"),
    ],
    "Congés payés": [
        ("L3141-1", "L3141-32"),
    ],
    "Contrat de travail (CDI, CDD)": [
        ("L1221-1", "L1221-26"),
        ("L1242-1", "L1242-17"),   # CDD : recours et durée
        ("L1243-1", "L1243-13"),   # CDD : rupture
    ],
    "Licenciement": [
        ("L1231-1", "L1231-7"),
        ("L1232-1", "L1232-14"),
        ("L1233-1", "L1233-30"),   # licenciement économique (partie principale)
        ("L1234-1", "L1234-20"),
        ("L1235-1", "L1235-18"),
    ],
    "Rupture conventionnelle": [
        ("L1237-11", "L1237-19"),
    ],
    "Salaire minimum (SMIC)": [
        ("L3231-1", "L3231-12"),
        ("L3232-1", "L3232-9"),
    ],
    "Représentation du personnel": [
        ("L2311-1", "L2311-2"),
        ("L2312-1", "L2312-40"),   # attributions du CSE (partie principale)
    ],
    "Harcèlement et discrimination": [
        ("L1152-1", "L1152-6"),
        ("L1153-1", "L1153-6"),
        ("L1154-1", "L1154-2"),
        ("L1155-1", "L1155-2"),
    ],
}