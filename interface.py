"""
Interface en ligne de commande — Jalon 5
Boucle interactive : saisie d'une question, affichage de la réponse,
des articles sources et de l'avertissement juridique. Sortie propre.
Affichage soigné avec la bibliothèque rich.
"""

import json

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from generation import generer_reponse, AVERTISSEMENT_JURIDIQUE
from constants import CORPUS_PATH

console = Console()

COMMANDES_SORTIE = {"quit", "exit", "q", "quitter"}


def lire_infos_corpus():
    """Date et taille du corpus, pour un affichage honnête (Q3 : fraîcheur)."""
    try:
        with open(CORPUS_PATH, encoding="utf-8") as f:
            corpus = json.load(f)
        return corpus[0].get("date_recuperation", "date inconnue"), len(corpus)
    except (FileNotFoundError, IndexError, json.JSONDecodeError):
        return "date inconnue", 0


def afficher_bienvenue():
    date_corpus, nb_articles = lire_infos_corpus()
    console.print()
    console.print(Panel.fit(
        "[bold]⚖️  ASSISTANT CODE DU TRAVAIL[/bold]\n"
        "[dim]Questions-réponses avec citation des articles[/dim]",
        border_style="blue",
    ))
    console.print(
        f"[dim]Corpus : {nb_articles} articles du Code du travail "
        f"(API Légifrance), à jour au [bold]{date_corpus}[/bold].\n"
        "Le droit évolue : vérifiez sur legifrance.gouv.fr que les articles "
        "cités sont toujours en vigueur.[/dim]"
    )
    console.print("[dim]Tapez votre question, ou [bold]quit[/bold] pour quitter.[/dim]\n")


def separer_avertissement(reponse_complete):
    """Sépare le corps de la réponse de l'avertissement (ajouté en code par
    la génération), pour pouvoir styliser chacun différemment."""
    if reponse_complete.endswith(AVERTISSEMENT_JURIDIQUE):
        corps = reponse_complete[: -len(AVERTISSEMENT_JURIDIQUE)].strip()
        return corps
    return reponse_complete


def afficher_reponse(resultat):
    corps = separer_avertissement(resultat["reponse"])

    # La réponse du modèle, en panneau vert
    console.print(Panel(
        Markdown(corps),
        title="[bold]Réponse[/bold]",
        border_style="green",
        padding=(1, 2),
    ))

    # Les articles sources (dédupliqués, ordre de pertinence conservé)
    sources_uniques = list(dict.fromkeys(resultat["articles_sources"]))
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_row(
        "[bold blue]📚 Articles consultés[/bold blue]",
        ", ".join(f"[cyan]{a}[/cyan]" for a in sources_uniques),
    )
    console.print(table)

    # L'avertissement juridique — TOUJOURS affiché, bien visible (Q5 + barème)
    console.print(Panel(
        f"[italic]{AVERTISSEMENT_JURIDIQUE}[/italic]",
        border_style="yellow",
        padding=(0, 2),
    ))


def boucle_principale():
    afficher_bienvenue()

    while True:
        try:
            question = console.input("[bold blue]❓ Votre question : [/bold blue]").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[dim]Au revoir ![/dim]")
            break

        if not question:
            continue

        if question.lower() in COMMANDES_SORTIE:
            console.print("[dim]Au revoir ![/dim]")
            break

        try:
            with console.status("[dim]Recherche dans le Code du travail...[/dim]", spinner="dots"):
                resultat = generer_reponse(question)
            afficher_reponse(resultat)
        except Exception as e:
            console.print(Panel(
                f"[red]Une erreur est survenue : {e}[/red]\n"
                "[dim]Vérifiez votre connexion et votre clé API, puis réessayez.[/dim]",
                border_style="red",
            ))


if __name__ == "__main__":
    boucle_principale()