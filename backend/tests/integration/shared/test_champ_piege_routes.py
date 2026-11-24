"""Champ piège des vraies routes d'écriture : refus avant le cas d'usage, rien n'est créé.

L'application réelle ne branche les protections qu'à l'étape de composition ; ce test
assemble donc les vrais routeurs avec la garde, comme la composition le fera.
"""

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from http import HTTPStatus
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.chantiers.api.routes import creer_routeur as creer_routeur_chantiers
from app.composition.base_de_donnees import BaseDeDonnees
from app.composition.chantiers import FournisseursChantiers
from app.composition.etapes import FournisseursEtapes
from app.etapes.api.routes import creer_routeur as creer_routeur_etapes
from app.shared.api.champ_piege import NOM_CHAMP_PIEGE
from app.shared.api.erreurs import enregistrer_gestionnaires_erreurs
from app.shared.infrastructure.adresses_bloquees_memoire import MemoireListeAdressesBloquees
from app.shared.infrastructure.generateur_uuid7 import GenerateurUuid7
from app.shared.infrastructure.memoire.horloge_avancable import HorlogeAvancable
from tests.conftest import url_sqlite
from tests.integration.conftest import CHANTIER_A_CREER, CHEF
from tests.integration.etapes.scenario import creer_chantier

ADRESSE = "testclient"
MESSAGE_NEUTRE = "Cette action n'est pas permise."


@pytest.fixture
def banc(tmp_path: Path) -> Iterator[tuple[TestClient, MemoireListeAdressesBloquees]]:
    horloge = HorlogeAvancable(datetime(2026, 11, 24, 9, 0, tzinfo=UTC))
    liste = MemoireListeAdressesBloquees(horloge, timedelta(hours=1))
    base = BaseDeDonnees(url_sqlite(tmp_path))
    generateur = GenerateurUuid7()
    application = FastAPI(lifespan=base.cycle_de_vie)
    enregistrer_gestionnaires_erreurs(application)
    chantiers = FournisseursChantiers(base.usine_sessions, generateur)
    etapes = FournisseursEtapes(base.usine_sessions, generateur)
    application.include_router(creer_routeur_chantiers(chantiers, liste), prefix="/api")
    application.include_router(creer_routeur_etapes(etapes, liste), prefix="/api")
    with TestClient(application) as client:
        yield client, liste


def test_un_chantier_avec_le_champ_piege_rempli_n_est_pas_cree(
    banc: tuple[TestClient, MemoireListeAdressesBloquees],
) -> None:
    client, liste = banc

    reponse = client.post(
        "/api/chantiers", json={**CHANTIER_A_CREER, NOM_CHAMP_PIEGE: "robot"}, headers=CHEF
    )

    assert reponse.status_code == HTTPStatus.FORBIDDEN
    assert reponse.json()["detail"] == MESSAGE_NEUTRE
    assert client.get("/api/chantiers", headers=CHEF).json() == []
    assert liste.est_bloquee(ADRESSE)


def test_une_etape_avec_le_champ_piege_rempli_n_est_pas_creee(
    banc: tuple[TestClient, MemoireListeAdressesBloquees],
) -> None:
    client, liste = banc
    chantier_id = creer_chantier(client)

    reponse = client.post(
        f"/api/chantiers/{chantier_id}/etapes",
        json={"titre": "Gros œuvre", NOM_CHAMP_PIEGE: "robot"},
        headers=CHEF,
    )

    assert reponse.status_code == HTTPStatus.FORBIDDEN
    assert client.get(f"/api/chantiers/{chantier_id}/etapes", headers=CHEF).json() == []
    assert liste.est_bloquee(ADRESSE)


def test_un_champ_piege_vide_est_accepte_et_n_est_jamais_renvoye(
    banc: tuple[TestClient, MemoireListeAdressesBloquees],
) -> None:
    client, liste = banc

    reponse = client.post(
        "/api/chantiers", json={**CHANTIER_A_CREER, NOM_CHAMP_PIEGE: ""}, headers=CHEF
    )

    assert reponse.status_code == HTTPStatus.CREATED
    assert NOM_CHAMP_PIEGE not in reponse.json()
    assert not liste.est_bloquee(ADRESSE)
