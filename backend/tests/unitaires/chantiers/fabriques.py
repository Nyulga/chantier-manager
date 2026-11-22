"""Fabriques de données de test fictives pour le module chantiers."""

from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID

from app.chantiers.application.creer_chantier import NouveauChantier
from app.chantiers.domain.adresse import Adresse
from app.chantiers.domain.chantier import Chantier, FicheChantier
from app.chantiers.domain.montant import Montant

NOM = "Rénovation école"
DEBUT = date(2026, 12, 1)
ECHEANCE = date(2027, 3, 31)
BUDGET = Decimal("125000.50")
# Instant des horloges fixes : neuf jours avant l'échéance, à 10 h en UTC.
MAINTENANT = datetime(2027, 3, 22, 10, 0, tzinfo=UTC)
JOURS_AVANT_ECHEANCE = 9
# Le soir de l'échéance, 22 h 30 en UTC : il est déjà 0 h 30 le lendemain à Paris (heure
# d'été, UTC+2). Le chantier y est donc en retard d'un jour, alors qu'en UTC ce serait
# encore le jour même.
LENDEMAIN_A_PARIS = datetime(2027, 3, 31, 22, 30, tzinfo=UTC)


CLIENT = "Mairie fictive"


def une_fiche(
    nom: str = NOM, date_debut: date = DEBUT, echeance: date = ECHEANCE, client: str = CLIENT
) -> FicheChantier:
    return FicheChantier(
        nom=nom,
        adresse=Adresse(voie="12 rue des Lilas", code_postal="69001", ville="Lyon"),
        client=client,
        date_debut=date_debut,
        echeance=echeance,
        budget=Montant(BUDGET),
    )


def un_chantier(numero: int = 1, nom: str = NOM) -> Chantier:
    return Chantier.creer(UUID(int=numero), une_fiche(nom=nom))


def une_commande(
    *,
    nom: str = NOM,
    ville: str = "Lyon",
    budget: Decimal = BUDGET,
    date_debut: date = DEBUT,
    echeance: date = ECHEANCE,
) -> NouveauChantier:
    return NouveauChantier(
        nom=nom,
        voie="12 rue des Lilas",
        code_postal="69001",
        ville=ville,
        client="Mairie fictive",
        date_debut=date_debut,
        echeance=echeance,
        budget=budget,
    )
