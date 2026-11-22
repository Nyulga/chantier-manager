from datetime import UTC, date, datetime
from uuid import UUID

import pytest

from app.shared.domain.erreurs import ValeurInvalideError
from app.shared.infrastructure.memoire.generateur_id_previsible import GenerateurIdPrevisible
from app.shared.infrastructure.memoire.horloge_fixe import HorlogeFixe
from app.shared.infrastructure.memoire.unit_of_work import MemoireEntrepot, MemoireUnitOfWork

INSTANT = datetime(2026, 11, 22, 8, 30, tzinfo=UTC)
CLE = UUID(int=1)


def un_uow() -> tuple[MemoireUnitOfWork, MemoireEntrepot[str]]:
    entrepot: MemoireEntrepot[str] = MemoireEntrepot()
    return MemoireUnitOfWork(entrepot), entrepot


def test_l_horloge_fixe_renvoie_toujours_le_meme_instant() -> None:
    horloge = HorlogeFixe(INSTANT)

    assert [horloge.maintenant(), horloge.maintenant()] == [INSTANT, INSTANT]


@pytest.mark.parametrize(
    ("instant", "date_a_paris"),
    [
        # Hiver (UTC+1) : 23 h 30 en UTC est déjà 0 h 30 le lendemain à Paris.
        (datetime(2026, 11, 22, 23, 30, tzinfo=UTC), date(2026, 11, 23)),
        # Été (UTC+2) : 22 h 30 en UTC est déjà 0 h 30 le lendemain à Paris.
        (datetime(2026, 6, 22, 22, 30, tzinfo=UTC), date(2026, 6, 23)),
        # Juste avant minuit à Paris, en hiver : on est encore le même jour.
        (datetime(2026, 11, 22, 22, 59, tzinfo=UTC), date(2026, 11, 22)),
        # Juste avant minuit à Paris, en été : on est encore le même jour.
        (datetime(2026, 6, 22, 21, 59, tzinfo=UTC), date(2026, 6, 22)),
    ],
    ids=["hiver-lendemain", "ete-lendemain", "hiver-meme-jour", "ete-meme-jour"],
)
def test_la_date_du_jour_de_l_horloge_fixe_est_celle_de_paris(
    instant: datetime, date_a_paris: date
) -> None:
    horloge = HorlogeFixe(instant)

    assert horloge.aujourd_hui() == date_a_paris


def test_le_generateur_previsible_renvoie_des_identifiants_croissants() -> None:
    generateur = GenerateurIdPrevisible()

    assert [generateur.nouveau(), generateur.nouveau()] == [UUID(int=1), UUID(int=2)]


def test_ce_qui_est_valide_est_conserve() -> None:
    uow, entrepot = un_uow()

    with uow:
        entrepot.elements[CLE] = "valeur"
        uow.valider()

    assert entrepot.elements == {CLE: "valeur"}
    assert uow.validations == 1


def test_sortir_sans_valider_annule_les_ecritures() -> None:
    uow, entrepot = un_uow()

    with uow:
        entrepot.elements[CLE] = "valeur"

    assert entrepot.elements == {}


def test_une_exception_annule_les_ecritures_et_remonte() -> None:
    uow, entrepot = un_uow()

    with pytest.raises(ValeurInvalideError), uow:
        entrepot.elements[CLE] = "valeur"
        raise ValeurInvalideError("Panne simulée au milieu de la transaction.")

    assert entrepot.elements == {}
    assert uow.validations == 0


def test_l_annulation_ne_touche_pas_aux_transactions_deja_validees() -> None:
    uow, entrepot = un_uow()
    with uow:
        entrepot.elements[CLE] = "valide"
        uow.valider()

    with uow:
        entrepot.elements[CLE] = "abandonne"

    assert entrepot.elements == {CLE: "valide"}
