"""Champ piège : rempli, il bloque l'adresse et refuse la requête avant la route."""

from datetime import UTC, datetime, timedelta
from http import HTTPStatus

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.shared.api.champ_piege import NOM_CHAMP_PIEGE, ChampPiege, creer_garde_champ_piege
from app.shared.api.erreurs import enregistrer_gestionnaires_erreurs
from app.shared.api.schemas import CONFIG_ENTREE
from app.shared.infrastructure.adresses_bloquees_memoire import MemoireListeAdressesBloquees
from app.shared.infrastructure.memoire.horloge_avancable import HorlogeAvancable

ADRESSE = "198.51.100.7"
MESSAGE_NEUTRE = "Cette action n'est pas permise."


class Formulaire(ChampPiege):
    model_config = CONFIG_ENTREE

    nom: str


class Sortie(BaseModel):
    nom: str


def un_client() -> tuple[TestClient, MemoireListeAdressesBloquees, list[Formulaire]]:
    horloge = HorlogeAvancable(datetime(2026, 11, 24, 9, 0, tzinfo=UTC))
    liste = MemoireListeAdressesBloquees(horloge, timedelta(hours=1))
    recus: list[Formulaire] = []
    application = FastAPI()
    enregistrer_gestionnaires_erreurs(application)
    garde = creer_garde_champ_piege(liste)

    @application.post("/formulaires", dependencies=[Depends(garde)], response_model=Sortie)
    def recevoir(formulaire: Formulaire) -> Sortie:
        recus.append(formulaire)
        return Sortie(nom=formulaire.nom)

    return TestClient(application, client=(ADRESSE, 5000)), liste, recus


@pytest.mark.parametrize("corps", [{"nom": "a"}, {"nom": "a", NOM_CHAMP_PIEGE: ""}])
def test_un_champ_piege_vide_ou_absent_laisse_passer(corps: dict[str, str]) -> None:
    client, liste, recus = un_client()

    reponse = client.post("/formulaires", json=corps)

    assert reponse.status_code == HTTPStatus.OK
    assert len(recus) == 1
    assert not liste.est_bloquee(ADRESSE)


@pytest.mark.parametrize("valeur", ["http://exemple.invalid", " ", 0, ["x"]])
def test_un_champ_piege_rempli_bloque_l_adresse_et_refuse_en_403_neutre(valeur: object) -> None:
    client, liste, recus = un_client()

    reponse = client.post("/formulaires", json={"nom": "a", NOM_CHAMP_PIEGE: valeur})

    assert reponse.status_code == HTTPStatus.FORBIDDEN
    assert reponse.headers["content-type"] == "application/problem+json"
    assert reponse.json()["detail"] == MESSAGE_NEUTRE
    assert recus == []
    assert liste.est_bloquee(ADRESSE)


def test_un_champ_piege_rempli_est_refuse_meme_si_le_reste_est_invalide() -> None:
    client, liste, _ = un_client()

    reponse = client.post("/formulaires", json={NOM_CHAMP_PIEGE: "x"})

    assert reponse.status_code == HTTPStatus.FORBIDDEN
    assert liste.est_bloquee(ADRESSE)


@pytest.mark.parametrize("contenu", [b"pas du json", b"[1, 2]", b'"texte"', b""])
def test_un_corps_sans_champ_piege_lisible_n_est_pas_bloque(contenu: bytes) -> None:
    client, liste, _ = un_client()

    reponse = client.post("/formulaires", content=contenu)

    assert reponse.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert not liste.est_bloquee(ADRESSE)


def test_le_champ_piege_est_documente_comme_a_ne_pas_remplir() -> None:
    propriete = ChampPiege.model_json_schema()["properties"][NOM_CHAMP_PIEGE]

    assert "ne pas remplir" in propriete["description"].lower()
