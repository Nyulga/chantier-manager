"""Unit of Work SQL : la seule classe qui ouvre, valide et annule une transaction."""

from types import TracebackType
from typing import Self

from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.orm.exc import StaleDataError

from app.shared.domain.erreurs import ConflitVersionError


class SqlUnitOfWork:
    """Implémentation SQL du port `UnitOfWork`, que chaque module étend avec ses repositories.

    Chaque entrée dans le bloc `with` ouvre une nouvelle session ; la sortie la
    ferme, ce qui annule tout ce qui n'a pas été validé. L'objet est donc
    réutilisable pour plusieurs transactions successives, mais pas simultanées :
    la composition en crée un par requête.
    """

    def __init__(self, usine_sessions: sessionmaker[Session]) -> None:
        self._usine_sessions = usine_sessions
        self._session: Session | None = None

    @property
    def session(self) -> Session:
        """La session de la transaction en cours, pour les repositories du module."""
        if self._session is None:
            raise RuntimeError("Le repository doit être utilisé dans un bloc `with uow:`.")
        return self._session

    def __enter__(self) -> Self:
        """Ouvre la transaction : une session neuve."""
        self._session = self._usine_sessions()
        return self

    def __exit__(
        self,
        type_erreur: type[BaseException] | None,
        erreur: BaseException | None,
        trace: TracebackType | None,
    ) -> None:
        """Ferme la session. Une transaction non validée est annulée par cette fermeture.

        L'exception éventuelle n'est pas absorbée : elle remonte à l'appelant.
        """
        session, self._session = self.session, None
        session.close()

    def valider(self) -> None:
        """Enregistre définitivement la transaction.

        Lève :
            ConflitVersionError : un objet a été modifié par quelqu'un d'autre depuis
                sa lecture (verrou optimiste, intent.md §2.3) ; rien n'est enregistré.
        """
        try:
            self.session.commit()
        except StaleDataError:
            raise ConflitVersionError(
                "Cet élément vient d'être modifié par quelqu'un d'autre : rechargez la page."
            ) from None
