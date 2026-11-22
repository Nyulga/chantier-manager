"""Conversions explicites entre les schémas JSON et les commandes et vues des cas d'usage."""

from uuid import UUID

from app.etapes.api.schemas import (
    ActiviteReponse,
    AjouterEtapeRequete,
    EtapeAValiderReponse,
    EtapeReponse,
    TransitionRequete,
)
from app.etapes.application.ajouter_etape import NouvelleEtape
from app.etapes.application.changer_statut_etape import ChangementStatut
from app.etapes.application.lister_activite_recente import DemandeActiviteRecente
from app.etapes.application.vues import ActiviteVue, EtapeAValiderVue, EtapeVue


def commande_ajout_depuis(chantier_id: UUID, requete: AjouterEtapeRequete) -> NouvelleEtape:
    """Convertit le corps de la requête en commande d'ajout."""
    return NouvelleEtape(chantier_id=chantier_id, titre=requete.titre)


def commande_statut_depuis(etape_id: UUID, requete: TransitionRequete) -> ChangementStatut:
    """Convertit le corps de la requête en commande de changement de statut."""
    return ChangementStatut(
        etape_id=etape_id, action=requete.action, commentaire=requete.commentaire
    )


def reponse_depuis(vue: EtapeVue) -> EtapeReponse:
    """Convertit la vue d'une étape en réponse JSON.

    Les statuts et les actions de la vue sont des chaînes : le modèle de réponse les
    valide contre les valeurs littérales de `schemas.py`, ce qui fait échouer tout
    de suite une valeur du domaine que l'API ne déclarerait pas encore.
    """
    return EtapeReponse.model_validate(vue, from_attributes=True)


def reponse_a_valider_depuis(vue: EtapeAValiderVue) -> EtapeAValiderReponse:
    """Convertit la vue d'une étape à valider en réponse JSON."""
    return EtapeAValiderReponse.model_validate(vue, from_attributes=True)


def demande_activite_depuis(limite: int) -> DemandeActiviteRecente:
    """Convertit le paramètre `limite` en demande ; le domaine en vérifie les bornes."""
    return DemandeActiviteRecente(limite=limite)


def reponse_activite_depuis(vue: ActiviteVue) -> ActiviteReponse:
    """Convertit une entrée du fil d'activité en réponse JSON."""
    return ActiviteReponse.model_validate(vue, from_attributes=True)
