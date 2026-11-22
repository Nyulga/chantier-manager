"""Assemblage des cas d'usage du module chantiers sur les implémentations SQL."""

from sqlalchemy.orm import Session, sessionmaker

from app.chantiers.application.consulter_chantier import ConsulterChantier
from app.chantiers.application.creer_chantier import CreerChantier
from app.chantiers.application.lister_chantiers import ListerChantiers
from app.chantiers.infrastructure.sql.unit_of_work import SqlUnitOfWorkChantiers
from app.etapes.application import CalculerAvancements
from app.etapes.infrastructure.sql.unit_of_work import SqlUnitOfWorkEtapes
from app.shared.application.ports import GenerateurId


class FournisseursChantiers:
    """Construit les cas d'usage de chantiers, avec leurs dépendances SQL.

    Chaque appel crée de nouveaux Unit of Work : une requête ne partage jamais sa
    transaction avec une autre. C'est ici, et seulement ici, que le port
    `FournisseurAvancement` de chantiers est branché sur le cas d'usage public
    `CalculerAvancements` d'étapes.
    """

    def __init__(self, usine_sessions: sessionmaker[Session], generateur_id: GenerateurId) -> None:
        self._usine_sessions = usine_sessions
        self._generateur_id = generateur_id

    def _uow(self) -> SqlUnitOfWorkChantiers:
        return SqlUnitOfWorkChantiers(self._usine_sessions)

    def _avancement(self) -> CalculerAvancements:
        return CalculerAvancements(SqlUnitOfWorkEtapes(self._usine_sessions))

    def creer_chantier(self) -> CreerChantier:
        """Fournit le cas d'usage de création."""
        return CreerChantier(self._uow(), self._generateur_id, self._avancement())

    def lister_chantiers(self) -> ListerChantiers:
        """Fournit le cas d'usage de liste."""
        return ListerChantiers(self._uow(), self._avancement())

    def consulter_chantier(self) -> ConsulterChantier:
        """Fournit le cas d'usage de consultation."""
        return ConsulterChantier(self._uow(), self._avancement())
