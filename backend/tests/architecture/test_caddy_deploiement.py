"""Garde l'alignement entre la copie locale, le bloc du serveur et le site statique.

Le Caddy du serveur n'a pas accès au dépôt : son bloc (`Caddyfile.extrait`) recopie
`protections.caddy`, que la copie locale importe. Sans ce test, une protection ajoutée d'un
seul côté passerait inaperçue, et le test d'intrusion local ne verrait plus ce que voit la
démo (constat M1 du premier pentest). Les fausses adresses doivent aussi rester celles de
l'API, et aucun port de l'API ne doit être publié (ADR 0015 : `--forwarded-allow-ips "*"`
n'est sûr que si seul le proxy peut joindre l'API).
"""

from pathlib import Path

from app.shared.api.pieges import CHEMINS_PIEGES

DEPLOY = Path(__file__).resolve().parents[3] / "deploy"
PROTECTIONS = DEPLOY / "protections.caddy"
EXTRAIT = DEPLOY / "Caddyfile.extrait"
LOCAL = DEPLOY / "Caddyfile.local"
STATIQUE = DEPLOY / "frontend.Caddyfile"
COMPOSE_PROD = DEPLOY / "compose.prod.yaml"
COMPOSE_LOCAL = DEPLOY / "compose.local.yaml"


def _lignes_utiles(fichier: Path) -> list[str]:
    """Donne les lignes de configuration : sans indentation, commentaires ni lignes vides."""
    lignes = (ligne.strip() for ligne in fichier.read_text(encoding="utf-8").splitlines())
    return [ligne for ligne in lignes if ligne and not ligne.startswith("#")]


def _bloc_header(fichier: Path) -> list[str]:
    """Donne le contenu du premier bloc `header { ... }` d'un fichier."""
    lignes = _lignes_utiles(fichier)
    debut = lignes.index("header {") + 1
    return lignes[debut : lignes.index("}", debut)]


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
