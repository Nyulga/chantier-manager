"""Erreurs 422 par champ : chemin lisible, message en français, jamais la valeur envoyée."""

from http import HTTPStatus
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, Field

from app.shared.api.erreurs import enregistrer_gestionnaires_erreurs
from app.shared.domain.erreurs import ValeurInvalideError

LONGUEUR_CODE_POSTAL = 5
AGE_MINIMAL = 18
TYPE_PROBLEME = "application/problem+json"


class AdresseRequete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code_postal: str = Field(max_length=LONGUEUR_CODE_POSTAL)


class CorpsRequete(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nom: str
    adresse: AdresseRequete
    age: int = Field(ge=AGE_MINIMAL)
    actif: bool = True


def une_application() -> FastAPI:
    application = FastAPI()
    enregistrer_gestionnaires_erreurs(application)

    def recevoir(corps: CorpsRequete) -> None:
        return None

    def refuser_un_champ() -> None:
        raise ValeurInvalideError("Le nom est obligatoire.", "nom")

    def refuser_sans_champ() -> None:
        raise ValeurInvalideError("L'échéance ne peut pas précéder le début.")

    application.add_api_route("/corps", recevoir, methods=["POST"])
    application.add_api_route("/refus-avec-champ", refuser_un_champ)
    application.add_api_route("/refus-sans-champ", refuser_sans_champ)
    return application


VALIDE: dict[str, Any] = {"nom": "Dupont", "adresse": {"code_postal": "69001"}, "age": 30}


def erreurs_de(corps: dict[str, Any]) -> list[dict[str, str]]:
    reponse = TestClient(une_application()).post("/corps", json=corps)
    assert reponse.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert reponse.headers["content-type"] == TYPE_PROBLEME
    erreurs: list[dict[str, str]] = reponse.json()["erreurs"]
    return erreurs


@pytest.mark.parametrize(
    ("corps", "champ", "message"),
    [
        ({**VALIDE, "nom": None}, "nom", "Ce champ doit être un texte."),
        (
            {"adresse": VALIDE["adresse"], "age": 30},
            "nom",
            "Ce champ est obligatoire.",
        ),
        (
            {**VALIDE, "adresse": {"code_postal": "690011"}},
            "adresse.code_postal",
            "Ce champ ne doit pas dépasser 5 caractères.",
        ),
        ({**VALIDE, "age": "abc"}, "age", "Ce champ doit être un nombre entier."),
        ({**VALIDE, "age": 12}, "age", "Ce champ doit être supérieur ou égal à 18."),
        ({**VALIDE, "pointure": 42}, "pointure", "Ce champ n'est pas attendu."),
        (
            {**VALIDE, "adresse": {"code_postal": "69001", "pointure": 42}},
            "adresse.pointure",
            "Ce champ n'est pas attendu.",
        ),
    ],
    ids=[
        "texte",
        "obligatoire",
        "trop-long-imbrique",
        "entier",
        "minimum",
        "inattendu-a-la-racine",
        "inattendu-imbrique",
    ],
)
def test_une_erreur_de_validation_designe_son_champ_avec_un_message_en_francais(
    corps: dict[str, Any], champ: str, message: str
) -> None:
    assert erreurs_de(corps) == [{"champ": champ, "message": message}]


def test_toutes_les_erreurs_sont_listees_et_le_detail_reste_global() -> None:
    reponse = TestClient(une_application()).post("/corps", json={"age": 3})

    assert reponse.json() == {
        "type": "about:blank",
        "title": "Données invalides",
        "status": HTTPStatus.UNPROCESSABLE_ENTITY,
        "detail": "Les données envoyées sont invalides.",
        "erreurs": [
            {"champ": "nom", "message": "Ce champ est obligatoire."},
            {"champ": "adresse", "message": "Ce champ est obligatoire."},
            {"champ": "age", "message": "Ce champ doit être supérieur ou égal à 18."},
        ],
    }


def test_un_type_d_erreur_sans_message_dedie_recoit_le_message_generique_sans_la_valeur() -> None:
    reponse = TestClient(une_application()).post("/corps", json={**VALIDE, "actif": "secret"})

    assert reponse.json()["erreurs"] == [
        {"champ": "actif", "message": "La valeur n'est pas valide."}
    ]
    assert "secret" not in reponse.text


def test_un_corps_qui_n_est_pas_du_json_donne_une_liste_d_erreurs_vide() -> None:
    reponse = TestClient(une_application()).post(
        "/corps", content="{secret", headers={"Content-Type": "application/json"}
    )

    assert reponse.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert reponse.json()["erreurs"] == []
    assert "secret" not in reponse.text


def test_une_erreur_du_domaine_qui_designe_un_champ_est_listee() -> None:
    reponse = TestClient(une_application()).get("/refus-avec-champ")

    assert reponse.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert reponse.headers["content-type"] == TYPE_PROBLEME
    assert reponse.json() == {
        "type": "about:blank",
        "title": "Données invalides",
        "status": HTTPStatus.UNPROCESSABLE_ENTITY,
        "detail": "Le nom est obligatoire.",
        "erreurs": [{"champ": "nom", "message": "Le nom est obligatoire."}],
    }


def test_une_erreur_du_domaine_sans_champ_a_une_liste_d_erreurs_vide() -> None:
    reponse = TestClient(une_application()).get("/refus-sans-champ")

    assert reponse.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert reponse.json()["detail"] == "L'échéance ne peut pas précéder le début."
    assert reponse.json()["erreurs"] == []


@pytest.mark.parametrize(
    "corps",
    [
        {**VALIDE, "jean.dupont@exemple.fr": 1},
        {**VALIDE, "adresse": {"code_postal": "69001", "jean.dupont@exemple.fr": 1}},
    ],
    ids=["racine", "imbrique"],
)
def test_une_cle_inventee_par_le_client_n_est_jamais_recopiee_dans_la_reponse(
    corps: dict[str, Any],
) -> None:
    reponse = TestClient(une_application()).post("/corps", json=corps)

    assert reponse.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert "jean.dupont" not in reponse.text


@pytest.mark.parametrize(
    "corps",
    [
        {**VALIDE, "jean@exemple.fr": 1},
        {**VALIDE, "a" * 65: 1},
        {**VALIDE, "1inconnu": 1},
        {**VALIDE, "mon champ": 1},
    ],
    ids=["adresse-email", "65-caracteres", "commence-par-un-chiffre", "espace"],
)
def test_une_cle_qui_n_a_pas_la_forme_d_un_nom_de_champ_designe_l_objet_qui_la_contient(
    corps: dict[str, Any],
) -> None:
    assert erreurs_de(corps) == [{"champ": "", "message": "Ce champ n'est pas attendu."}]


def test_une_cle_de_64_caracteres_a_la_forme_d_un_nom_de_champ() -> None:
    nom = "a" * 64

    assert erreurs_de({**VALIDE, nom: 1}) == [
        {"champ": nom, "message": "Ce champ n'est pas attendu."}
    ]
