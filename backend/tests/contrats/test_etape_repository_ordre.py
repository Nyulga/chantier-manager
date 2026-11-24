"""Contrat du port `EtapeRepository` sur l'ordre des étapes : tri et unicité par chantier."""

from dataclasses import replace
from uuid import UUID

import pytest

from app.etapes.application.ports import UnitOfWorkEtapes
from app.shared.domain.erreurs import ConflitVersionError
from tests.contrats.conftest import AUTRE_CHANTIER
from tests.contrats.enregistrement_etapes import enregistrer
from tests.fabriques.etapes import ID_CHANTIER, id_etape, une_etape

AUTRE_IDENTIFIANT = UUID(int=999)


def test_a_ordre_egal_les_etapes_de_deux_chantiers_sont_departagees_par_identifiant(
    uow_etapes: UnitOfWorkEtapes,
) -> None:
    enregistrer(
        uow_etapes,
        une_etape(ordre=1, chantier_id=AUTRE_CHANTIER),
        une_etape(ordre=1),
    )

    with uow_etapes:
        etapes = uow_etapes.etapes.lister_par_chantiers([AUTRE_CHANTIER, ID_CHANTIER])

    assert [etape.id for etape in etapes] == [id_etape(1), id_etape(1, AUTRE_CHANTIER)]


def test_deux_etapes_de_meme_ordre_dans_un_chantier_sont_refusees_dans_la_meme_transaction(
    uow_etapes: UnitOfWorkEtapes,
) -> None:
    premiere = une_etape(ordre=1)
    doublon = replace(premiere, id=AUTRE_IDENTIFIANT)

    with pytest.raises(ConflitVersionError):
        enregistrer(uow_etapes, premiere, doublon)

    with uow_etapes:
        assert uow_etapes.etapes.lister_par_chantiers([ID_CHANTIER]) == []


def test_un_ordre_deja_pris_par_une_etape_enregistree_est_refuse(
    uow_etapes: UnitOfWorkEtapes,
) -> None:
    premiere = une_etape(ordre=1)
    enregistrer(uow_etapes, premiere)

    with pytest.raises(ConflitVersionError):
        enregistrer(uow_etapes, replace(premiere, id=AUTRE_IDENTIFIANT))

    with uow_etapes:
        etapes = uow_etapes.etapes.lister_par_chantiers([ID_CHANTIER])
    assert [etape.id for etape in etapes] == [premiere.id]


def test_le_meme_ordre_est_permis_dans_deux_chantiers_differents(
    uow_etapes: UnitOfWorkEtapes,
) -> None:
    enregistrer(uow_etapes, une_etape(ordre=1), une_etape(ordre=1, chantier_id=AUTRE_CHANTIER))

    with uow_etapes:
        etapes = uow_etapes.etapes.lister_par_chantiers([ID_CHANTIER, AUTRE_CHANTIER])

    assert {etape.chantier_id for etape in etapes} == {ID_CHANTIER, AUTRE_CHANTIER}
