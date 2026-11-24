"""Unit of Work SQL utilisée hors de son bloc `with`."""

import pytest
from sqlalchemy.orm import Session, sessionmaker

from app.shared.infrastructure.sql.unit_of_work import SqlUnitOfWork


def test_utiliser_la_session_hors_d_un_bloc_with_est_une_erreur_de_programmation(
    usine_sessions: sessionmaker[Session],
) -> None:
    uow = SqlUnitOfWork(usine_sessions)

    with pytest.raises(RuntimeError, match="with"):
        _ = uow.session
