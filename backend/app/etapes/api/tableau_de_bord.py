"""Routes du tableau de bord : étapes à valider et fil d'activité, sans logique métier."""

from http import HTTPStatus
from typing import Annotated, Any, Protocol

from fastapi import APIRouter, Depends, Query, Response

from app.etapes.api.conversions import (
    demande_activite_depuis,
    reponse_a_valider_depuis,
    reponse_activite_depuis,
    valeur_en_tete_tronquee,
)
from app.etapes.api.schemas import ActiviteReponse, EtapeAValiderReponse
from app.etapes.application.lister_activite_recente import (
    DemandeActiviteRecente,
    ListerActiviteRecente,
)
from app.etapes.application.lister_etapes_a_valider import ListerEtapesAValider
from app.shared.api.acteur import ActeurCourant
from app.shared.api.documentation_erreurs import erreurs_documentees

# La valeur par défaut est celle du cas d'usage, lue sur la commande : une seule source.
# Les bornes sont vérifiées par le cas d'usage, qui répond 422 (`ValeurInvalideError`).
LIMITE_PAR_DEFAUT = DemandeActiviteRecente.limite
DESCRIPTION_LIMITE = (
    "Nombre d'entrées voulues, de la plus récente à la plus ancienne. "
    "Une valeur hors des bornes du fil d'activité est refusée (422)."
)
ERREURS = erreurs_documentees(
    HTTPStatus.BAD_REQUEST,
    HTTPStatus.FORBIDDEN,
    HTTPStatus.UNPROCESSABLE_ENTITY,
    HTTPStatus.TOO_MANY_REQUESTS,
    HTTPStatus.SERVICE_UNAVAILABLE,
)

# L'indicateur de liste coupée voyage dans un en-tête, pour que le corps reste une simple
# liste : les clients qui ne le lisent pas ne sont pas touchés.
EN_TETE_TRONQUEE = "X-Liste-Tronquee"
REPONSE_A_VALIDER: dict[int | str, dict[str, Any]] = {
    HTTPStatus.OK.value: {
        "description": "Les étapes à valider, de la plus anciennement signalée à la plus récente.",
        "headers": {
            EN_TETE_TRONQUEE: {
                "description": (
                    "`true` si d'autres étapes attendent une décision sans figurer dans la "
                    "liste, coupée à son plafond : l'écran affiche alors un total approché."
                ),
                "schema": {"type": "string", "enum": ["true", "false"]},
            }
        },
    }
}


class CasUsagesTableauDeBord(Protocol):
    """Les cas d'usage que la composition root fournit aux routes du tableau de bord."""

    def lister_etapes_a_valider(self) -> ListerEtapesAValider:
        """Fournit le cas d'usage de la liste « À valider »."""
        ...

    def lister_activite_recente(self) -> ListerActiviteRecente:
        """Fournit le cas d'usage du fil d'activité."""
        ...


def creer_routeur_tableau_de_bord(cas_usages: CasUsagesTableauDeBord) -> APIRouter:
    """Crée le routeur du tableau de bord.

    Il est inclus dans le routeur des étapes avant les routes `/etapes/{etape_id}`, pour
    que le chemin fixe `/etapes/a-valider` ne puisse jamais être pris pour un
    identifiant d'étape : `tests/integration/etapes/test_ordre_des_routes.py` le vérifie.
    """
    routeur = APIRouter(tags=["étapes"], responses=ERREURS)

    @routeur.get(
        "/etapes/a-valider",
        status_code=HTTPStatus.OK,
        response_model=list[EtapeAValiderReponse],
        responses=REPONSE_A_VALIDER,
        summary="Liste les étapes qui attendent la décision d'un chef",
    )
    def lister_a_valider(
        acteur: ActeurCourant,
        reponse: Response,
        cas_usage: Annotated[ListerEtapesAValider, Depends(cas_usages.lister_etapes_a_valider)],
    ) -> list[EtapeAValiderReponse]:
        liste = cas_usage.executer(acteur)
        reponse.headers[EN_TETE_TRONQUEE] = valeur_en_tete_tronquee(liste.tronquee)
        return [reponse_a_valider_depuis(vue) for vue in liste.etapes]

    @routeur.get(
        "/activite",
        status_code=HTTPStatus.OK,
        response_model=list[ActiviteReponse],
        summary="Liste les derniers changements de statut des étapes",
    )
    def lister_activite(
        acteur: ActeurCourant,
        cas_usage: Annotated[ListerActiviteRecente, Depends(cas_usages.lister_activite_recente)],
        limite: Annotated[int, Query(description=DESCRIPTION_LIMITE)] = LIMITE_PAR_DEFAUT,
    ) -> list[ActiviteReponse]:
        demande = demande_activite_depuis(limite)
        return [reponse_activite_depuis(vue) for vue in cas_usage.executer(demande, acteur)]

    return routeur
