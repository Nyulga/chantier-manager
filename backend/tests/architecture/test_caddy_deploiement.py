"""Garde l'alignement entre la copie locale, le bloc du serveur et le site statique.

Le Caddy du serveur n'a pas accès au dépôt : son bloc (`Caddyfile.extrait`) recopie
`protections.caddy`, que la copie locale importe. Sans ce test, une protection ajoutée d'un
seul côté passerait inaperçue, et le test d'intrusion local ne verrait plus ce que voit la
démo (constat M1 du premier pentest). Les fausses adresses doivent aussi rester celles de
l'API, et aucun port de l'API ne doit être publié (ADR 0015 : `--forwarded-allow-ips "*"`
n'est sûr que si seul le proxy peut joindre l'API).
"""

from pathlib import Path

import pytest

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


def _lignes_utiles(fichier: Path) -> list[str]:
    """Donne les lignes de configuration : sans indentation, commentaires ni lignes vides."""
    lignes = (ligne.strip() for ligne in fichier.read_text(encoding="utf-8").splitlines())
    return [ligne for ligne in lignes if ligne and not ligne.startswith("#")]


def _bloc_header(fichier: Path) -> list[str]:
    """Donne le contenu du premier bloc `header { ... }` d'un fichier."""
    lignes = _lignes_utiles(fichier)
    debut = lignes.index("header {") + 1
    return lignes[debut : lignes.index("}", debut)]


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
