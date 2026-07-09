# test_connexion_api.py — Vérifie que l'authentification OAuth2 fonctionne

from legifrance_client import LegifranceClient

client = LegifranceClient()
jeton = client._get_token()
print(f"✅ Connexion réussie ! Début du jeton : {jeton[:20]}...")