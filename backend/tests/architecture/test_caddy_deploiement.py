"""Garde l'alignement entre la copie locale, le bloc du serveur et le site statique.

Le Caddy du serveur n'a pas accès au dépôt : son bloc (`Caddyfile.extrait`) recopie
`protections.caddy`, que la copie locale importe. Sans ce test, une protection ajoutée d'un
seul côté passerait inaperçue, et le test d'intrusion local ne verrait plus ce que voit la
démo (constat M1 du premier pentest). Les fausses adresses doivent aussi rester celles de
l'API, et aucun port de l'API ne doit être publié (ADR 0015 : `--forwarded-allow-ips "*"`
n'est sûr que si seul le proxy peut joindre l'API).
"""

import json
import re
from http import HTTPStatus
from pathlib import Path

import pytest

from app.composition.parametres import TAILLE_MAX_CORPS
from app.shared.api.erreurs import (
    MESSAGE_CORPS_TROP_VOLUMINEUX,
    MESSAGE_ERREUR_HTTP,
    TYPE_PROBLEME,
    reponse_probleme,
)
from app.shared.api.pieges import CHEMINS_PIEGES

DEPLOY = Path(__file__).resolve().parents[3] / "deploy"
PROTECTIONS = DEPLOY / "protections.caddy"
EXTRAIT = DEPLOY / "Caddyfile.extrait"
LOCAL = DEPLOY / "Caddyfile.local"
STATIQUE = DEPLOY / "frontend.Caddyfile"
COMPOSE_PROD = DEPLOY / "compose.prod.yaml"
COMPOSE_LOCAL = DEPLOY / "compose.local.yaml"
# Le limiteur de débit et le blocage de l'API comptent par adresse : le proxy doit donc imposer
# l'adresse de la connexion, quelle que soit la configuration globale du Caddy du serveur
# (par exemple des `trusted_proxies`), sinon un visiteur changerait d'adresse à volonté (ADR 0016).
EN_TETE_ADRESSE_CLIENT = "header_up X-Forwarded-For {remote_host}"
# Deux routes vont à l'API : les fausses adresses de robots et `/api/*`.
ROUTES_VERS_L_API = 2
# Unités de taille que Caddy comprend (bibliothèque go-humanize) : `KB` compte 1000 octets et
# `KiB` 1024. Une unité absente de cette table est refusée, plutôt que devinée.
OCTETS_PAR_UNITE = {"B": 1, "KB": 1000, "KiB": 1024, "MB": 1000**2, "MiB": 1024**2}
BLOC_ERREURS = "handle_errors {"
# Une réponse d'erreur du proxy : `respond`, un corps JSON entre apostrophes inverses, le statut.
REPONSE_PROBLEME = re.compile(r"respond `(\{.*\})` (\S+)")
# Statut de la réponse générique : celui de l'erreur en cours, que Caddy remplace à l'exécution.
STATUT_DU_PROXY = "{err.status_code}"
# Un statut que l'API ne nomme pas : la réponse générique du proxy doit égaler celle de l'API.
STATUT_SANS_TITRE = HTTPStatus.IM_A_TEAPOT


def _lignes_utiles(fichier: Path) -> list[str]:
    """Donne les lignes de configuration : sans indentation, commentaires ni lignes vides."""
    lignes = (ligne.strip() for ligne in fichier.read_text(encoding="utf-8").splitlines())
    return [ligne for ligne in lignes if ligne and not ligne.startswith("#")]


def _bloc_header(fichier: Path, apres: str | None = None) -> list[str]:
    """Donne le contenu du premier bloc `header { ... }`, en cherchant après la ligne `apres`."""
    lignes = _lignes_utiles(fichier)
    depart = lignes.index(apres) if apres else 0
    debut = lignes.index("header {", depart) + 1
    return lignes[debut : lignes.index("}", debut)]


def _octets(taille: str) -> int:
    """Convertit une taille écrite comme Caddy la lit (`64KiB`) en octets.

    Lève :
        ValueError : l'unité est absente ou inconnue.
    """
    correspondance = re.fullmatch(r"(\d+)([A-Za-z]+)", taille)
    if correspondance is None or correspondance[2] not in OCTETS_PAR_UNITE:
        raise ValueError(f"Taille ou unité inconnue : {taille}")
    return int(correspondance[1]) * OCTETS_PAR_UNITE[correspondance[2]]


def _reponses_probleme(fichier: Path) -> dict[str, str]:
    """Donne, par statut écrit dans le fichier, le corps JSON des réponses d'erreur du proxy."""
    trouvees = (REPONSE_PROBLEME.fullmatch(ligne) for ligne in _lignes_utiles(fichier))
    return {trouvee[2]: trouvee[1] for trouvee in trouvees if trouvee}


def _corps_de_l_api(statut: int, detail: str) -> object:
    """Donne le corps JSON que l'API renvoie pour ce statut et ce détail."""
    return json.loads(bytes(reponse_probleme(statut, detail).body))


def _blocs_vers_l_api(fichier: Path) -> list[list[str]]:
    """Donne les lignes du bloc de chaque `reverse_proxy` vers l'API (vide s'il n'en a pas)."""
    lignes = _lignes_utiles(fichier)
    blocs: list[list[str]] = []
    for position, ligne in enumerate(lignes):
        if not ligne.startswith("reverse_proxy chantier-api:"):
            continue
        fin = lignes.index("}", position) if ligne.endswith("{") else position
        blocs.append(lignes[position + 1 : fin])
    return blocs


def test_le_bloc_du_serveur_recopie_les_protections_de_la_copie_locale() -> None:
    extrait = _lignes_utiles(EXTRAIT)

    assert extrait[0].endswith(" {")
    assert extrait[1:-1] == _lignes_utiles(PROTECTIONS)
    assert extrait[-1] == "}"


def test_la_copie_locale_importe_les_protections() -> None:
    assert "import /etc/caddy/protections.caddy" in _lignes_utiles(LOCAL)
    assert "- ./protections.caddy:/etc/caddy/protections.caddy:ro" in _lignes_utiles(COMPOSE_LOCAL)


def test_les_fausses_adresses_du_proxy_sont_celles_de_l_api() -> None:
    chemins = [c for chemin in CHEMINS_PIEGES for c in (chemin, f"{chemin}/*")]
    attendu = "@pieges path " + " ".join(chemins)

    assert attendu in _lignes_utiles(PROTECTIONS)
    assert "handle @pieges {" in _lignes_utiles(PROTECTIONS)


def test_le_site_statique_pose_les_memes_en_tetes_que_le_proxy() -> None:
    assert _bloc_header(STATIQUE) == _bloc_header(PROTECTIONS)


def test_aucun_port_n_est_publie_en_production() -> None:
    assert not [ligne for ligne in _lignes_utiles(COMPOSE_PROD) if ligne.startswith("ports:")]


@pytest.mark.parametrize("fichier", [PROTECTIONS, EXTRAIT], ids=lambda fichier: fichier.name)
def test_le_proxy_force_l_adresse_du_client_pour_l_api(fichier: Path) -> None:
    # La copie locale importe `protections.caddy` : ce fichier est donc sa copie locale.
    blocs = _blocs_vers_l_api(fichier)

    assert len(blocs) == ROUTES_VERS_L_API
    assert [bloc for bloc in blocs if EN_TETE_ADRESSE_CLIENT not in bloc] == []


def test_la_limite_de_taille_du_proxy_est_celle_de_l_api() -> None:
    valeurs = [
        ligne.split()[1] for ligne in _lignes_utiles(PROTECTIONS) if ligne.startswith("max_size ")
    ]

    assert [_octets(valeur) for valeur in valeurs] == [TAILLE_MAX_CORPS]


@pytest.mark.parametrize(
    ("taille", "octets"),
    [("64KiB", 65_536), ("64KB", 64_000), ("2MiB", 2_097_152), ("2MB", 2_000_000), ("5B", 5)],
)
def test_les_unites_de_taille_sont_converties_comme_le_fait_caddy(taille: str, octets: int) -> None:
    assert _octets(taille) == octets


@pytest.mark.parametrize("taille", ["64Ko", "64K", "64", "64kib", "KiB", "64 KiB"])
def test_une_unite_de_taille_inconnue_est_refusee(taille: str) -> None:
    with pytest.raises(ValueError, match="inconnue"):
        _octets(taille)


def test_le_proxy_repond_a_ses_propres_erreurs_au_format_de_l_application() -> None:
    lignes = _lignes_utiles(PROTECTIONS)

    assert BLOC_ERREURS in lignes
    assert f"header Content-Type {TYPE_PROBLEME}" in lignes


def test_les_erreurs_du_proxy_portent_les_memes_en_tetes_que_ses_reponses_normales() -> None:
    # Le `header` du site ne s'applique pas aux erreurs du proxy : le bloc doit être répété,
    # et rien ne doit pouvoir diverger entre les deux (en-têtes posés, `Server` et `Via` retirés).
    normales = _bloc_header(PROTECTIONS)
    erreurs = _bloc_header(PROTECTIONS, apres=BLOC_ERREURS)

    assert erreurs == normales
    assert {"-Server", "-Via"} <= set(erreurs)


def test_le_413_du_proxy_a_le_titre_et_le_message_de_l_api() -> None:
    reponses = _reponses_probleme(PROTECTIONS)

    attendu = _corps_de_l_api(HTTPStatus.CONTENT_TOO_LARGE, MESSAGE_CORPS_TROP_VOLUMINEUX)
    assert json.loads(reponses[str(HTTPStatus.CONTENT_TOO_LARGE.value)]) == attendu


def test_les_autres_erreurs_du_proxy_ont_la_reponse_generique_de_l_api() -> None:
    reponses = _reponses_probleme(PROTECTIONS)

    corps = reponses[STATUT_DU_PROXY].replace(STATUT_DU_PROXY, str(STATUT_SANS_TITRE.value))
    assert json.loads(corps) == _corps_de_l_api(STATUT_SANS_TITRE, MESSAGE_ERREUR_HTTP)
    assert set(reponses) == {str(HTTPStatus.CONTENT_TOO_LARGE.value), STATUT_DU_PROXY}
