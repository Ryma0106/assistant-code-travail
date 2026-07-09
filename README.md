# Assistant Code du travail (RAG)

Projet final M2 MD5 — Data & IA

## Binôme
- Ryma BEN MANSOUR (Ryma0106)
- Licia ATTOUCHE (liciaatt)

## Questions de réflexion

### 1. Granularité du chunking

**Notre choix : approche hybride — un chunk par article, enrichi du contexte de sa section.**

Chunking par section : les chunks seraient trop longs, l'embedding "moyennerait" plusieurs sujets et le retrieval perdrait en précision. Chunking par article seul : précis, mais un article qui renvoie à un autre ("au sens de l'article L1234-5...") devient incompréhensible isolé.

Nous indexons donc **un chunk = un article**, mais le texte embeddé contient aussi le **titre de la section thématique** (ex : "Durée du travail — Article L3121-1 : ..."), et la section est stockée en **métadonnée**. On garde la précision du retrieval article par article, la facilité de citation, et un contexte thématique qui aide l'embedding.

### 2. Traçabilité

**Notre choix : le numéro d'article est stocké aux deux endroits — dans le texte embeddé ET dans les métadonnées.**

Dans les métadonnées : c'est la source fiable, le code peut afficher les sources sans dépendre du LLM. Dans le texte embeddé : le LLM voit le numéro dans son contexte et peut le citer, et les recherches du type "que dit L3121-1 ?" matchent mieux.

Pour empêcher le LLM d'inventer des numéros : le prompt système lui interdit de citer un article absent du contexte fourni, et le contexte est numéroté avec les vrais identifiants. En complément, l'affichage des sources sous la réponse vient **des métadonnées** (du code, pas du LLM) : même si le LLM se trompait, l'utilisateur voit les vraies références.

### 3. Fraîcheur

**Notre choix : dater le corpus et l'afficher dans l'interface.**

La date de récupération est enregistrée dans chaque document du corpus au moment de sa constitution, et l'indexation détecte tout changement du corpus par empreinte (hash) pour réindexer uniquement si nécessaire. Les interfaces affichent : "Corpus à jour au [date]. Le droit du travail évolue : vérifiez sur legifrance.gouv.fr que les articles cités sont toujours en vigueur." Le système est ainsi honnête sur son obsolescence possible sans prétendre se mettre à jour tout seul.

### 4. Réponses conditionnelles

**Notre choix : réponse générale assortie de réserves explicites.**

Beaucoup de règles dépendent de la taille de l'entreprise ou de la convention collective. Le prompt système impose : donner la règle générale du Code, puis signaler explicitement les conditions ("ce seuil peut différer selon votre convention collective ou l'effectif de l'entreprise") quand les articles récupérés mentionnent de telles conditions. Nous avons écarté la question de clarification systématique : en ligne de commande, elle alourdit l'échange, et l'utilisateur n'a pas toujours l'information demandée.

### 5. La frontière du conseil juridique

**Notre choix : répondre au factuel, rediriger l'interprétatif.**

Une question factuelle ("combien de jours de congés par an ?") trouve sa réponse directement dans un article : le système répond en citant. Une question d'interprétation ("mon licenciement est-il abusif ?") demande d'appliquer le droit à une situation personnelle : c'est du conseil juridique, que le système ne doit pas donner. Le prompt instruit le LLM de reconnaître ces cas et d'y répondre en citant les articles pertinents à titre informatif, tout en renvoyant vers un avocat ou l'inspection du travail. L'avertissement juridique obligatoire est de plus ajouté **par le code** à chaque réponse (pas seulement par le prompt), car un LLM peut oublier une consigne "une fois sur dix" — la garantie doit être dans le pipeline, pas dans la bonne volonté du modèle.

## Installation

### Prérequis
- Python 3.12
- Un compte [PISTE](https://piste.gouv.fr) avec souscription à l'API Légifrance (production)
- Une clé API [Groq](https://console.groq.com)

### Étapes

1. Cloner le dépôt :
```bash
git clone https://github.com/Ryma0106/assistant-code-travail.git
cd assistant-code-travail
```

2. Créer et activer l'environnement virtuel :
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

3. Installer les dépendances :
```bash
python -m pip install -r requirements.txt
```

4. Configurer les clés : copier `.env.example` en `.env` et renseigner
`GROQ_API_KEY`, `LEGIFRANCE_CLIENT_ID`, `LEGIFRANCE_CLIENT_SECRET`.
⚠️ Le fichier `.env` ne doit jamais être commité (il est dans le `.gitignore`).

⚠️ **Windows** : si Python s'arrête silencieusement au chargement du modèle
d'embedding, installer PyTorch en build CPU
(`pip install torch --index-url https://download.pytorch.org/whl/cpu`)
et vérifier la taille du fichier de pagination Windows.

## Utilisation

### 1. Construire le corpus (une seule fois — facultatif, le corpus est versionné)
```bash
python build_corpus.py
```
Récupère ~300 articles du Code du travail sur 8 thèmes via l'API Légifrance
(~25 min, requêtes volontairement espacées). Résultat : `data/corpus.json`.

### 2. Contrôler la qualité du corpus
```bash
python controle_qualite.py
```

### 3. Indexer le corpus
```bash
python indexation.py
```
Encode les articles et persiste la base ChromaDB. Au relancement, la base est
rechargée sans réindexation (détection de changement du corpus par hash).

### 4. Vérifier le retrieval (optionnel)
```bash
python test_retrieval.py
```
Jeu d'évaluation : 5 questions dont l'article attendu est connu — validé 5/5.

### 5. Poser des questions — interface en ligne de commande
```bash
python interface.py
```
Réponses avec citations, articles sources, avertissement juridique
systématique. Sortie : `quit`.

### 6. Poser des questions — interface web (bonus)
```bash
streamlit run app_web.py
```
Historique de conversation, badges d'articles cliquables vers Légifrance,
détail des chunks avec distances (score de confiance).