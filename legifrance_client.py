# legifrance_client.py — Client pour l'API Légifrance (OAuth2 client credentials)

import os
import time

import requests
from dotenv import load_dotenv

from constants import LEGIFRANCE_TOKEN_URL, LEGIFRANCE_API_BASE_URL


class LegifranceClient:
    def __init__(self):
        load_dotenv()
        self.client_id = os.getenv("LEGIFRANCE_CLIENT_ID")
        self.client_secret = os.getenv("LEGIFRANCE_CLIENT_SECRET")
        if not self.client_id or not self.client_secret:
            raise ValueError(
                "LEGIFRANCE_CLIENT_ID / LEGIFRANCE_CLIENT_SECRET absents du .env"
            )

        self._token = None
        self._token_expiration = 0  # timestamp d'expiration du jeton

    def _get_token(self):
        """Récupère un jeton OAuth2, en le renouvelant s'il a expiré
        (le sujet insiste : le jeton expire, il faut prévoir le renouvellement !)."""
        # Si on a déjà un jeton encore valable, on le réutilise
        if self._token and time.time() < self._token_expiration:
            return self._token

        # Sinon, on échange client_id + client_secret contre un nouveau jeton
        reponse = requests.post(
            LEGIFRANCE_TOKEN_URL,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": "openid",
            },
        )
        reponse.raise_for_status()
        donnees = reponse.json()

        self._token = donnees["access_token"]
        # On garde 60 secondes de marge avant l'expiration réelle
        self._token_expiration = time.time() + donnees.get("expires_in", 3600) - 60
        print("🎫 Nouveau jeton OAuth2 obtenu")
        return self._token

    def post(self, endpoint, payload):
        """Appelle un point d'accès de l'API Légifrance avec le jeton."""
        jeton = self._get_token()
        reponse = requests.post(
            f"{LEGIFRANCE_API_BASE_URL}{endpoint}",
            json=payload,
            headers={"Authorization": f"Bearer {jeton}"},
        )
        reponse.raise_for_status()
        return reponse.json()