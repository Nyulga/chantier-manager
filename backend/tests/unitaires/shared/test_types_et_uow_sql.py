from datetime import UTC, datetime, timedelta, timezone

import pytest
from sqlalchemy.dialects import sqlite
from sqlalchemy.orm import Session, sessionmaker

from app.shared.infrastructure.sql.types import DateHeureUtc
from app.shared.infrastructure.sql.unit_of_work import SqlUnitOfWork

PARIS = timezone(timedelta(hours=1))
DIALECTE = sqlite.dialect()


def test_une_date_est_convertie_en_utc_avant_l_enregistrement() -> None:
    type_colonne = DateHeureUtc()

    valeur = type_colonne.process_bind_param(datetime(2026, 11, 22, 10, 0, tzinfo=PARIS), DIALECTE)

    assert valeur == datetime(2026, 11, 22, 9, 0, tzinfo=UTC)
    assert valeur is not None
    assert valeur.utcoffset() == timedelta(0)


def test_une_date_sans_fuseau_est_refusee_a_l_enregistrement() -> None:
    with pytest.raises(ValueError, match="fuseau"):
        DateHeureUtc().process_bind_param(datetime(2026, 11, 22, 10, 0), DIALECTE)


def test_une_date_relue_sans_fuseau_est_en_utc() -> None:
    valeur = DateHeureUtc().process_result_value(datetime(2026, 11, 22, 9, 0), DIALECTE)

    assert valeur == datetime(2026, 11, 22, 9, 0, tzinfo=UTC)


def test_l_absence_de_date_reste_absente() -> None:
    type_colonne = DateHeureUtc()

    assert type_colonne.process_bind_param(None, DIALECTE) is None
    assert type_colonne.process_result_value(None, DIALECTE) is None


def test_une_date_deja_localisee_est_relue_telle_quelle() -> None:
    instant = datetime(2026, 11, 22, 9, 0, tzinfo=UTC)

    assert DateHeureUtc().process_result_value(instant, DIALECTE) == instant


def test_utiliser_la_session_hors_d_un_bloc_with_est_une_erreur_de_programmation(
    usine_sessions: sessionmaker[Session],
) -> None:
    uow = SqlUnitOfWork(usine_sessions)

    with pytest.raises(RuntimeError, match="with"):
        _ = uow.session
