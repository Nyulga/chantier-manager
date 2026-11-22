"""Conversions explicites entre les schémas JSON et les commandes et vues des cas d'usage."""

from app.chantiers.api.schemas import AdresseReponse, ChantierReponse, CreerChantierRequete
from app.chantiers.application.creer_chantier import NouveauChantier
from app.chantiers.application.vues import ChantierVue


def commande_depuis(requete: CreerChantierRequete) -> NouveauChantier:
    """Convertit le corps de la requête en commande de création."""
    return NouveauChantier(
        nom=requete.nom,
        voie=requete.adresse.voie,
        code_postal=requete.adresse.code_postal,
        ville=requete.adresse.ville,
        client=requete.client,
        date_debut=requete.date_debut,
        echeance=requete.echeance,
        budget=requete.budget,
    )


def reponse_depuis(vue: ChantierVue) -> ChantierReponse:
    """Convertit la vue d'un chantier en réponse JSON."""
    return ChantierReponse(
        id=vue.id,
        nom=vue.nom,
        adresse=AdresseReponse(
            voie=vue.adresse.voie, code_postal=vue.adresse.code_postal, ville=vue.adresse.ville
        ),
        client=vue.client,
        date_debut=vue.date_debut,
        echeance=vue.echeance,
        budget=vue.budget,
        avancement=vue.avancement,
        peut_ajouter_etape=vue.peut_ajouter_etape,
    )
