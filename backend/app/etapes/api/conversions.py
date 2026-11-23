"""Conversions explicites entre les schémas JSON et les commandes et vues des cas d'usage.

Les vues portent leurs statuts, rôles et actions sous forme de chaînes, car l'api ne
connaît pas le domaine. Chaque réponse est donc construite champ par champ, puis validée
par son modèle : une valeur du domaine que l'API ne déclarerait pas encore (un nouveau
statut, par exemple) fait échouer tout de suite, au lieu d'être exposée sans être typée.
"""

from uuid import UUID

from app.etapes.api.schemas import (
    ActiviteReponse,
    AjouterEtapeRequete,
    CapacitesReponse,
    EtapeAValiderReponse,
    EtapeReponse,
    TransitionRequete,
)
from app.etapes.application.ajouter_etape import NouvelleEtape
from app.etapes.application.changer_statut_etape import ChangementStatut
from app.etapes.application.lister_activite_recente import DemandeActiviteRecente
from app.etapes.application.vues import ActiviteVue, CapacitesVue, EtapeAValiderVue, EtapeVue


def commande_ajout_depuis(chantier_id: UUID, requete: AjouterEtapeRequete) -> NouvelleEtape:
    """Convertit le corps de la requête en commande d'ajout."""
    return NouvelleEtape(chantier_id=chantier_id, titre=requete.titre)


def commande_statut_depuis(etape_id: UUID, requete: TransitionRequete) -> ChangementStatut:
    """Convertit le corps de la requête en commande de changement de statut."""
    return ChangementStatut(
        etape_id=etape_id,
        action=requete.action,
        commentaire=requete.commentaire,
        version_attendue=requete.version,
    )


def reponse_depuis(vue: EtapeVue) -> EtapeReponse:
    """Convertit la vue d'une étape en réponse JSON."""
    return EtapeReponse.model_validate(
        {
            "id": vue.id,
            "chantier_id": vue.chantier_id,
            "titre": vue.titre,
            "ordre": vue.ordre,
            "statut": vue.statut,
            "version": vue.version,
            "actions_permises": list(vue.actions_permises),
        }
    )


def reponse_a_valider_depuis(vue: EtapeAValiderVue) -> EtapeAValiderReponse:
    """Convertit la vue d'une étape à valider en réponse JSON."""
    return EtapeAValiderReponse.model_validate(
        {
            "id": vue.id,
            "chantier_id": vue.chantier_id,
            "titre": vue.titre,
            "version": vue.version,
            "actions_permises": list(vue.actions_permises),
            "signalee_le": vue.signalee_le,
        }
    )


def valeur_en_tete_tronquee(tronquee: bool) -> str:
    """Écrit l'indicateur de liste coupée tel qu'il figure dans l'en-tête HTTP."""
    return str(tronquee).lower()


def demande_activite_depuis(limite: int) -> DemandeActiviteRecente:
    """Convertit le paramètre `limite` en demande ; le domaine en vérifie les bornes."""
    return DemandeActiviteRecente(limite=limite)


def reponse_activite_depuis(vue: ActiviteVue) -> ActiviteReponse:
    """Convertit une entrée du fil d'activité en réponse JSON."""
    return ActiviteReponse.model_validate(
        {
            "etape_id": vue.etape_id,
            "chantier_id": vue.chantier_id,
            "titre_etape": vue.titre_etape,
            "role": vue.role,
            "ancien_statut": vue.ancien_statut,
            "nouveau_statut": vue.nouveau_statut,
            "date": vue.date,
            "commentaire": vue.commentaire,
        }
    )


def reponse_capacites_depuis(vue: CapacitesVue) -> CapacitesReponse:
    """Convertit la vue des capacités de l'acteur en réponse JSON."""
    return CapacitesReponse.model_validate(
        {
            "role": vue.role,
            "peut_creer_chantier": vue.peut_creer_chantier,
            "peut_lister_etapes_a_valider": vue.peut_lister_etapes_a_valider,
        }
    )
