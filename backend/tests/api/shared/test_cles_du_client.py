"""Clés de comptage du client : bloc /64 habituel, seconde clé par bloc /48, jamais d'exception."""

import pytest

from app.shared.api.acces_http import ADRESSE_INCONNUE, cle_du_bloc_48, cle_du_client
from app.shared.api.pieges import est_chemin_piege


def _portee(adresse: str) -> dict[str, object]:
    return {"client": (adresse, 5000)}


@pytest.mark.parametrize(
    ("adresse", "cle"),
    [
        ("192.0.2.10", "192.0.2.10"),
        ("::ffff:192.0.2.10", "192.0.2.10"),
        ("2001:db8:1:2:3::5", "2001:db8:1:2::/64"),
        ("::1", "::/64"),
        ("fe80::1%eth0", "fe80::/64"),
    ],
)
def test_la_cle_habituelle_est_l_ipv4_ou_le_bloc_64(adresse: str, cle: str) -> None:
    assert cle_du_client(_portee(adresse)) == cle


@pytest.mark.parametrize("adresse", ["fe80::1%a/b", "fe80::1%/", "testclient", ""])
def test_une_adresse_illisible_donne_une_cle_et_jamais_une_exception(adresse: str) -> None:
    assert cle_du_client(_portee(adresse)) == adresse
    assert cle_du_bloc_48(_portee(adresse)) is None


@pytest.mark.parametrize(
    ("adresse", "cle"),
    [
        ("2001:db8:1:2:3::5", "2001:db8:1::/48"),
        ("2001:db8:1:ffff::9", "2001:db8:1::/48"),
        ("::1", "::/48"),
        ("fe80::1%eth0", "fe80::/48"),
    ],
)
def test_une_ipv6_a_une_seconde_cle_par_bloc_48(adresse: str, cle: str) -> None:
    assert cle_du_bloc_48(_portee(adresse)) == cle


@pytest.mark.parametrize("adresse", ["192.0.2.10", "::ffff:192.0.2.10", "testclient"])
def test_une_ipv4_ou_une_adresse_illisible_n_a_pas_de_seconde_cle(adresse: str) -> None:
    assert cle_du_bloc_48(_portee(adresse)) is None


@pytest.mark.parametrize("portee", [{"client": None}, {}])
def test_sans_adresse_de_client_il_n_y_a_pas_de_seconde_cle(portee: dict[str, object]) -> None:
    assert cle_du_client(portee) == ADRESSE_INCONNUE
    assert cle_du_bloc_48(portee) is None


@pytest.mark.parametrize(
    "chemin",
    [
        "/wp-admin",
        "/WP-ADMIN",
        "/Wp-Login.PHP",
        "/.ENV",
        "/.GIT/config",
        "/.git/",
        "/phpMyAdmin/index.php",
        "/XMLRPC.php",
    ],
)
def test_un_chemin_piege_est_reconnu_sans_tenir_compte_de_la_casse(chemin: str) -> None:
    assert est_chemin_piege(chemin)


@pytest.mark.parametrize(
    "chemin",
    ["/", "/api/chantiers", "/API/chantiers", "/api/wp-admin", "/wp-administrator", "/.gitignore"],
)
def test_un_chemin_legitime_n_est_jamais_pris_pour_un_piege(chemin: str) -> None:
    assert not est_chemin_piege(chemin)
