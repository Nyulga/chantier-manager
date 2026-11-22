"""Fabriques de données de test fictives pour le module étapes."""

from datetime import UTC, datetime
from uuid import UUID

from app.etapes.domain.cycle import StatutEtape
from app.etapes.domain.etape import Etape

INSTANT = datetime(2026, 11, 22, 9, 0, tzinfo=UTC)
ID_CHANTIER = UUID(int=100)
ETAPES_PAR_CHANTIER = 1000


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
