"""Champ piège des formulaires : un champ que seul un robot remplit.

Un humain ne voit jamais ce champ ; un robot qui remplit tous les champs d'un formulaire
l'écrit aussi. Le remplir bloque l'adresse et refuse la requête avant le cas d'usage, qui
ne reçoit donc jamais ce champ.
"""

import json
from collections.abc import Awaitable, Callable
from email.message import Message
from http import HTTPStatus

from fastapi import Depends, HTTPException, Request, params
from pydantic import BaseModel, Field

from app.shared.api.acces_http import cle_du_client
from app.shared.api.schemas import CONFIG_ENTREE
from app.shared.application.ports import ListeAdressesBloquees

NOM_CHAMP_PIEGE = "site_web"
TYPE_PRINCIPAL_JSON = "application"


class ChampPiege(BaseModel):
    """Base des schémas d'entrée qui portent le champ piège.

    Le champ est déclaré pour que `extra="forbid"` ne le refuse pas en 422 (un 422 ne
    bloquerait personne), et pour le documenter dans OpenAPI : il ne sert qu'à piéger.
    Les conversions vers les commandes ne le recopient jamais.
    """

    model_config = CONFIG_ENTREE

    site_web: str | None = Field(
        default=None,
        description="Champ piège : ne pas remplir. Il doit rester vide ou absent.",
    )


def creer_garde_champ_piege(liste: ListeAdressesBloquees) -> Callable[[Request], Awaitable[None]]:
    """Crée la dépendance qui refuse en 403 un corps dont le champ piège est rempli.

    Elle lit le corps brut plutôt que le schéma validé : un robot qui remplit le piège est
    bloqué même si le reste du formulaire est invalide, au lieu de recevoir un 422 qui lui
    dirait de réessayer. Starlette garde le corps en cache : la route le relit sans coût.

    Lève (par la dépendance renvoyée) :
        HTTPException : 403, le champ piège est rempli ; l'adresse est alors bloquée.
    """

    async def verifier(requete: Request) -> None:
        if _est_du_json(requete) and _champ_piege_rempli(await requete.body()):
            liste.bloquer(cle_du_client(requete.scope))
            raise HTTPException(status_code=HTTPStatus.FORBIDDEN)

    return verifier


def dependances_champ_piege(liste: ListeAdressesBloquees) -> list[params.Depends]:
    """Donne les `dependencies` d'une route d'écriture qui porte le champ piège.

    La liste est obligatoire : une garde facultative serait une protection qu'on peut
    oublier de brancher.
    """
    return [Depends(creer_garde_champ_piege(liste))]


def _est_du_json(requete: Request) -> bool:
    # Même critère que FastAPI pour lire un corps comme du JSON : `application/json` ou tout
    # sous-type `json` / `…+json`. Un autre critère laisserait passer un robot qui envoie
    # `application/merge-patch+json`. Ces types exigent une pré-vérification CORS dans un
    # navigateur : un site tiers ne peut pas les envoyer à l'insu du visiteur, donc la
    # protection contre le blocage d'un innocent reste intacte (ADR 0016). `text/plain` et
    # `text/json`, eux, ne sont jamais examinés.
    message = Message()
    message["content-type"] = requete.headers.get("content-type", "")
    if message.get_content_maintype() != TYPE_PRINCIPAL_JSON:
        return False
    sous_type = message.get_content_subtype()
    return sous_type == "json" or sous_type.endswith("+json")


def _champ_piege_rempli(corps: bytes) -> bool:
    # Un corps illisible n'est pas un robot piégé : la validation de la route le refusera en 422.
    try:
        contenu = json.loads(corps)
    except ValueError:
        return False
    return isinstance(contenu, dict) and contenu.get(NOM_CHAMP_PIEGE) not in (None, "")
