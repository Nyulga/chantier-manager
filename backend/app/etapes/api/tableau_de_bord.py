"""Routes du tableau de bord : étapes à valider et fil d'activité, sans logique métier."""

from typing import Annotated, Protocol

from fastapi import APIRouter, Depends, Query

from app.etapes.api.conversions import (
    demande_activite_depuis,
    reponse_a_valider_depuis,
    reponse_activite_depuis,
)
from app.etapes.api.schemas import ActiviteReponse, EtapeAValiderReponse
from app.etapes.application.lister_activite_recente import (
    DemandeActiviteRecente,
    ListerActiviteRecente,
)
from app.etapes.application.lister_etapes_a_valider import ListerEtapesAValider
from app.shared.api.acteur import ActeurCourant

# La valeur par défaut est celle du domaine, lue sur la commande : une seule source.
# Les bornes sont vérifiées par le domaine, qui répond 422 (`ValeurInvalideError`).
LIMITE_PAR_DEFAUT = DemandeActiviteRecente.limite
DESCRIPTION_LIMITE = (
    "Nombre d'entrées voulues, de la plus récente à la plus ancienne. "
    "Une valeur hors des bornes du fil d'activité est refusée (422)."
)


class FournisseursTableauDeBord(Protocol):
    """Les cas d'usage que la composition root fournit aux routes du tableau de bord."""

    def lister_etapes_a_valider(self) -> ListerEtapesAValider:
        """Fournit le cas d'usage de la liste « À valider »."""
        ...

    def lister_activite_recente(self) -> ListerActiviteRecente:
        """Fournit le cas d'usage du fil d'activité."""
        ...


def creer_routeur_tableau_de_bord(fournisseurs: FournisseursTableauDeBord) -> APIRouter:
    """Crée le routeur du tableau de bord.

    Il est inclus dans le routeur des étapes, qui lui apporte les erreurs documentées
    et le tag OpenAPI. La route `/etapes/a-valider` est un chemin fixe : aucune route
    `/etapes/{id}` ne peut la capturer, et un test le vérifie.
    """
    routeur = APIRouter()

    @routeur.get(
        "/etapes/a-valider", summary="Liste les étapes qui attendent la décision d'un chef"
    )
    def lister_a_valider(
        acteur: ActeurCourant,
        cas_usage: Annotated[ListerEtapesAValider, Depends(fournisseurs.lister_etapes_a_valider)],
    ) -> list[EtapeAValiderReponse]:
        return [reponse_a_valider_depuis(vue) for vue in cas_usage.executer(acteur)]

    @routeur.get("/activite", summary="Liste les derniers changements de statut des étapes")
    def lister_activite(
        acteur: ActeurCourant,
        cas_usage: Annotated[ListerActiviteRecente, Depends(fournisseurs.lister_activite_recente)],
        limite: Annotated[int, Query(description=DESCRIPTION_LIMITE)] = LIMITE_PAR_DEFAUT,
    ) -> list[ActiviteReponse]:
        demande = demande_activite_depuis(limite)
        return [reponse_activite_depuis(vue) for vue in cas_usage.executer(demande, acteur)]

    return routeur
