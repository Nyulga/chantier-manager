"""Assemblage des cas d'usage du module étapes sur les implémentations SQL."""

from sqlalchemy.orm import Session, sessionmaker

from app.chantiers.application import AutoriserAjoutEtape, VerifierChantierExiste
from app.chantiers.infrastructure.sql.unit_of_work import SqlUnitOfWorkChantiers
from app.etapes.application.ajouter_etape import AjouterEtape
from app.etapes.application.changer_statut_etape import ChangerStatutEtape
from app.etapes.application.lister_etapes import ListerEtapes
from app.etapes.infrastructure.sql.unit_of_work import SqlUnitOfWorkEtapes
from app.shared.application.ports import GenerateurId
from app.shared.infrastructure.horloge_systeme import HorlogeSysteme


class FournisseursEtapes:
    """Construit les cas d'usage d'étapes, avec leurs dépendances SQL.

    Les ports `VerificationChantier` et `AutorisationAjoutEtape` d'étapes sont
    branchés ici sur les cas d'usage publics de chantiers : étapes n'importe rien
    de chantiers. Chaque appel crée de nouveaux Unit of Work, un par requête.
    """

    def __init__(self, usine_sessions: sessionmaker[Session], generateur_id: GenerateurId) -> None:
        self._usine_sessions = usine_sessions
        self._generateur_id = generateur_id

    def _uow(self) -> SqlUnitOfWorkEtapes:
        return SqlUnitOfWorkEtapes(self._usine_sessions)

    def _chantiers(self) -> SqlUnitOfWorkChantiers:
        return SqlUnitOfWorkChantiers(self._usine_sessions)

    def lister_etapes(self) -> ListerEtapes:
        """Fournit le cas d'usage de liste."""
        return ListerEtapes(self._uow(), VerifierChantierExiste(self._chantiers()))

    def ajouter_etape(self) -> AjouterEtape:
        """Fournit le cas d'usage d'ajout."""
        return AjouterEtape(
            self._uow(), self._generateur_id, AutoriserAjoutEtape(self._chantiers())
        )

    def changer_statut_etape(self) -> ChangerStatutEtape:
        """Fournit le cas d'usage de changement de statut."""
        return ChangerStatutEtape(self._uow(), HorlogeSysteme())
