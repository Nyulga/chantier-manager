"""Une erreur 500 ne laisse dans le journal aucune valeur envoyée à la base (issue #16)."""

import traceback
from dataclasses import replace
from http import HTTPStatus
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.composition.mapping import metadonnees
from app.etapes.infrastructure.sql.unit_of_work import SqlUnitOfWorkEtapes
from app.shared.api.erreurs import enregistrer_gestionnaires_erreurs
from app.shared.infrastructure.sql.moteur import creer_moteur, creer_usine_sessions
from tests.conftest import url_sqlite
from tests.fabriques.etapes import une_etape

TITRE_CONFIDENTIEL = "titre-confidentiel-a-ne-jamais-journaliser"


def application_qui_viole_une_cle_etrangere(tmp_path: Path) -> FastAPI:
    """Application dont une route enregistre une étape rattachée à un chantier inexistant."""
    moteur = creer_moteur(url_sqlite(tmp_path))
    metadonnees().create_all(moteur)
    usine = creer_usine_sessions(moteur)
    application = FastAPI()
    enregistrer_gestionnaires_erreurs(application)

    def enregistrer() -> None:
        with SqlUnitOfWorkEtapes(usine) as uow:
            uow.etapes.ajouter(replace(une_etape(), titre=TITRE_CONFIDENTIEL))
            uow.valider()

    application.add_api_route("/enregistrer", enregistrer, methods=["POST"])
    return application


def test_une_violation_de_cle_etrangere_donne_un_500_dont_le_journal_ne_cite_aucune_valeur(
    tmp_path: Path,
) -> None:
    client = TestClient(application_qui_viole_une_cle_etrangere(tmp_path))

    # Le client de test relève l'exception du serveur : c'est elle que le serveur écrirait
    # dans son journal, avec sa trace complète.
    with pytest.raises(IntegrityError) as erreur:
        client.post("/enregistrer")
    journal = "".join(traceback.format_exception(erreur.value))

    assert "FOREIGN KEY" in journal
    assert TITRE_CONFIDENTIEL not in journal


def test_la_reponse_500_ne_cite_aucune_valeur(tmp_path: Path) -> None:
    client = TestClient(
        application_qui_viole_une_cle_etrangere(tmp_path), raise_server_exceptions=False
    )

    reponse = client.post("/enregistrer")

    assert reponse.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert TITRE_CONFIDENTIEL not in reponse.text
