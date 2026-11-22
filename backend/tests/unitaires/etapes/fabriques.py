"""Fabriques de données de test fictives pour le module étapes."""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.etapes.domain.cycle import ActionEtape, StatutEtape
from app.etapes.domain.etape import Etape
from app.shared.domain.acteur import Acteur, Role

INSTANT = datetime(2026, 11, 22, 9, 0, tzinfo=UTC)
ID_CHANTIER = UUID(int=100)
ETAPES_PAR_CHANTIER = 1000
OUVRIER = Acteur(Role.OUVRIER)


def id_etape(ordre: int, chantier_id: UUID = ID_CHANTIER) -> UUID:
    """Identifiant prévisible et distinct d'un chantier à l'autre."""
    return UUID(int=chantier_id.int * ETAPES_PAR_CHANTIER + ordre)


def une_etape(
    statut: StatutEtape = StatutEtape.A_FAIRE, ordre: int = 1, chantier_id: UUID = ID_CHANTIER
) -> Etape:
    return Etape(
        id=id_etape(ordre, chantier_id),
        chantier_id=chantier_id,
        titre="Gros œuvre",
        ordre=ordre,
        statut=statut,
    )


def heures_apres(heures: int) -> datetime:
    """Instant situé quelques heures après `INSTANT`, pour ordonner des transitions."""
    return INSTANT + timedelta(hours=heures)


def une_etape_signalee(
    signalee_le: datetime, ordre: int = 1, chantier_id: UUID = ID_CHANTIER
) -> Etape:
    """Étape démarrée une heure avant son signalement, puis signalée terminée par un ouvrier.

    Elle passe par le vrai cycle du domaine : son historique est donc complet.
    """
    etape = une_etape(ordre=ordre, chantier_id=chantier_id)
    etape.appliquer(ActionEtape.DEMARRER, OUVRIER, signalee_le - timedelta(hours=1))
    etape.appliquer(ActionEtape.SIGNALER_TERMINEE, OUVRIER, signalee_le)
    return etape
