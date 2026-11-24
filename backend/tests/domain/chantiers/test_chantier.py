"""Agrégat `Chantier` et sa fiche : création et invariants (champs obligatoires, bornes, dates)."""

from datetime import date
from uuid import UUID

import pytest

from app.chantiers.domain.chantier import Chantier
from app.shared.domain.erreurs import ValeurInvalideError
from tests.fabriques.chantiers import DEBUT, une_fiche

ID_CHANTIER = UUID(int=42)


def test_creer_un_chantier_reprend_l_identifiant_et_la_fiche() -> None:
    fiche = une_fiche()

    chantier = Chantier.creer(ID_CHANTIER, fiche)

    assert chantier == Chantier(
        id=ID_CHANTIER,
        nom=fiche.nom,
        adresse=fiche.adresse,
        client=fiche.client,
        date_debut=fiche.date_debut,
        echeance=fiche.echeance,
        budget=fiche.budget,
    )


@pytest.mark.parametrize("nom", ["", "   ", "\n"])
def test_une_fiche_sans_nom_est_refusee(nom: str) -> None:
    with pytest.raises(ValeurInvalideError):
        une_fiche(nom=nom)


@pytest.mark.parametrize("client", ["", "   ", "\t\n"])
def test_une_fiche_sans_client_est_refusee(client: str) -> None:
    with pytest.raises(ValeurInvalideError):
        une_fiche(client=client)


def test_un_nom_et_un_client_de_200_caracteres_sont_acceptes() -> None:
    fiche = une_fiche(nom="n" * 200, client="c" * 200)

    assert (len(fiche.nom), len(fiche.client)) == (200, 200)


@pytest.mark.parametrize(
    ("nom", "client"),
    [("n" * 201, "Mairie fictive"), ("Rénovation", "c" * 201)],
    ids=["nom", "client"],
)
def test_un_nom_ou_un_client_de_plus_de_200_caracteres_est_refuse(nom: str, client: str) -> None:
    with pytest.raises(ValeurInvalideError):
        une_fiche(nom=nom, client=client)


def test_une_echeance_anterieure_au_debut_est_refusee() -> None:
    with pytest.raises(ValeurInvalideError):
        une_fiche(date_debut=date(2026, 12, 2), echeance=date(2026, 12, 1))


def test_une_echeance_le_jour_du_debut_est_acceptee() -> None:
    fiche = une_fiche(echeance=DEBUT)

    assert fiche.echeance == fiche.date_debut


@pytest.mark.parametrize(
    ("nom", "client", "echeance", "champ_fautif"),
    [
        ("", "Mairie", date(2027, 1, 1), "nom"),
        ("n" * 201, "Mairie", date(2027, 1, 1), "nom"),
        ("Rénovation", " ", date(2027, 1, 1), "client"),
        ("Rénovation", "c" * 201, date(2027, 1, 1), "client"),
        ("Rénovation", "Mairie", date(2026, 11, 30), "echeance"),
    ],
    ids=["nom-vide", "nom-long", "client-vide", "client-long", "echeance"],
)
def test_une_fiche_refusee_designe_le_champ_fautif(
    nom: str, client: str, echeance: date, champ_fautif: str
) -> None:
    with pytest.raises(ValeurInvalideError) as erreur:
        une_fiche(nom=nom, client=client, date_debut=date(2026, 12, 1), echeance=echeance)

    assert erreur.value.champ == champ_fautif
