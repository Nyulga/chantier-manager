"""Traduction centrale des erreurs en réponses RFC 9457, et acteur tiré de `X-Profil`."""

from collections.abc import Callable
from http import HTTPStatus

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.shared.api.acteur import ActeurCourant
from app.shared.api.erreurs import enregistrer_gestionnaires_erreurs, journal
from app.shared.application.erreurs import ServiceIndisponibleError
from app.shared.domain.erreurs import (
    AccesRefuseError,
    ConflitVersionError,
    NonTrouveError,
    TransitionInterditeError,
)

TYPE_PROBLEME = "application/problem+json"


def une_application() -> FastAPI:
    application = FastAPI()
    enregistrer_gestionnaires_erreurs(application)
    erreurs = {
        "non-trouve": NonTrouveError("Chantier introuvable."),
        "acces-refuse": AccesRefuseError("Accès refusé."),
        "transition": TransitionInterditeError("Transition impossible."),
        "conflit": ConflitVersionError("Modifié entre-temps."),
    }
    for nom, erreur in erreurs.items():
        application.add_api_route(f"/erreur/{nom}", route_qui_leve(erreur))
    application.add_api_route("/inconnue", route_qui_leve(RuntimeError("secret interne")))
    application.add_api_route("/profil", lire_profil)
    return application


def route_qui_leve(erreur: Exception) -> Callable[[], None]:
    def route() -> None:
        raise erreur

    return route


def lire_profil(acteur: ActeurCourant) -> dict[str, str]:
    return {"role": acteur.role.value}


@pytest.mark.parametrize(
    ("chemin", "statut", "message"),
    [
        ("non-trouve", HTTPStatus.NOT_FOUND, "Chantier introuvable."),
        ("acces-refuse", HTTPStatus.FORBIDDEN, "Accès refusé."),
        ("transition", HTTPStatus.CONFLICT, "Transition impossible."),
        ("conflit", HTTPStatus.CONFLICT, "Modifié entre-temps."),
    ],
)
def test_une_erreur_metier_devient_un_probleme_http_en_francais(
    chemin: str, statut: HTTPStatus, message: str
) -> None:
    client = TestClient(une_application())

    reponse = client.get(f"/erreur/{chemin}")

    assert reponse.status_code == statut
    assert reponse.headers["content-type"] == TYPE_PROBLEME
    assert reponse.json() == {
        "type": "about:blank",
        "title": reponse.json()["title"],
        "status": statut,
        "detail": message,
    }


def test_une_erreur_inconnue_donne_un_500_generique_sans_detail_interne() -> None:
    client = TestClient(une_application(), raise_server_exceptions=False)

    reponse = client.get("/inconnue")

    assert reponse.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert reponse.headers["content-type"] == TYPE_PROBLEME
    assert "secret interne" not in reponse.text
    assert reponse.json()["detail"] == "Une erreur interne est survenue."


@pytest.mark.parametrize("profil", ["chef", "ouvrier"])
def test_le_profil_de_l_en_tete_devient_l_acteur(profil: str) -> None:
    client = TestClient(une_application())

    reponse = client.get("/profil", headers={"X-Profil": profil})

    assert reponse.json() == {"role": profil}


@pytest.mark.parametrize("en_tetes", [{}, {"X-Profil": "directeur"}, {"X-Profil": ""}])
def test_un_profil_absent_ou_inconnu_donne_un_400(en_tetes: dict[str, str]) -> None:
    client = TestClient(une_application())

    reponse = client.get("/profil", headers=en_tetes)

    assert reponse.status_code == HTTPStatus.BAD_REQUEST
    assert reponse.headers["content-type"] == TYPE_PROBLEME
    assert reponse.json()["detail"] == "L'en-tête X-Profil doit valoir « chef » ou « ouvrier »."


def test_une_requete_mal_formee_donne_un_422_sans_echo_de_la_valeur_envoyee() -> None:
    application = une_application()
    application.add_api_route("/nombre", lire_nombre)
    client = TestClient(application)

    reponse = client.get("/nombre", params={"valeur": "confidentiel"})

    assert reponse.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert reponse.headers["content-type"] == TYPE_PROBLEME
    assert "confidentiel" not in reponse.text


def lire_nombre(valeur: int) -> int:
    return valeur


def test_un_identifiant_mal_forme_dans_le_chemin_donne_un_404_sans_echo() -> None:
    application = une_application()
    application.add_api_route("/nombre/{valeur}", lire_nombre)
    client = TestClient(application)

    reponse = client.get("/nombre/confidentiel")

    assert reponse.status_code == HTTPStatus.NOT_FOUND
    assert reponse.headers["content-type"] == TYPE_PROBLEME
    assert reponse.json()["detail"] == "Cette ressource n'existe pas."
    assert "confidentiel" not in reponse.text


def test_une_route_inconnue_donne_un_404_au_format_rfc_9457() -> None:
    client = TestClient(une_application())

    reponse = client.get("/nulle-part")

    assert reponse.status_code == HTTPStatus.NOT_FOUND
    assert reponse.headers["content-type"] == TYPE_PROBLEME
    assert reponse.json() == {
        "type": "about:blank",
        "title": "Ressource introuvable",
        "status": HTTPStatus.NOT_FOUND,
        "detail": "Cette ressource n'existe pas.",
    }


def test_une_methode_non_permise_donne_un_405_qui_annonce_les_methodes_permises() -> None:
    client = TestClient(une_application())

    reponse = client.post("/profil")

    assert reponse.status_code == HTTPStatus.METHOD_NOT_ALLOWED
    assert reponse.headers["content-type"] == TYPE_PROBLEME
    assert reponse.headers["allow"] == "GET"
    assert reponse.json()["detail"] == "Cette méthode n'est pas permise sur cette ressource."


def test_un_service_indisponible_donne_un_503_generique_sans_la_cause(
    caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Les tests d'architecture lancent import-linter, dont la configuration des journaux
    # désactive ceux qui existent déjà : on réactive celui des erreurs pour ce test.
    monkeypatch.setattr(journal, "disabled", False)
    application = une_application()
    erreur = ServiceIndisponibleError("Base de données inaccessible.")
    erreur.__cause__ = RuntimeError("base verrouillée")
    application.add_api_route("/indisponible", route_qui_leve(erreur))
    client = TestClient(application)

    reponse = client.get("/indisponible")

    assert reponse.status_code == HTTPStatus.SERVICE_UNAVAILABLE
    assert reponse.headers["content-type"] == TYPE_PROBLEME
    assert reponse.json() == {
        "type": "about:blank",
        "title": "Service indisponible",
        "status": HTTPStatus.SERVICE_UNAVAILABLE,
        "detail": "Le service est momentanément indisponible : réessaie dans un instant.",
    }
    assert "base verrouillée" not in reponse.text
    # Le journal du serveur garde le message de la cause, pour diagnostiquer la panne.
    assert "RuntimeError: base verrouillée" in caplog.text
