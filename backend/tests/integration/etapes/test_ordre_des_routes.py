"""Ordre d'enregistrement des routes des étapes dans l'application complète."""

from pathlib import Path

from fastapi.routing import iter_route_contexts

from app.composition.parametres import Parametres
from app.main import creer_application
from tests.conftest import url_sqlite

CHEMIN_A_VALIDER = "/api/etapes/a-valider"
PREFIXE_PARAMETRE = "/api/etapes/{"


def test_le_chemin_fixe_a_valider_precede_toute_route_etapes_parametree(tmp_path: Path) -> None:
    # Les routes sont essayées dans l'ordre d'enregistrement : le chemin fixe doit passer
    # avant tout `/etapes/{…}`, sinon « a-valider » pourrait être lu comme un identifiant.
    # FastAPI range les routeurs inclus derrière des enveloppes : `iter_route_contexts`
    # les déplie dans l'ordre où la requête les essaie.
    application = creer_application(Parametres(url_base=url_sqlite(tmp_path)))

    chemins = [str(contexte.path) for contexte in iter_route_contexts(application.routes)]
    positions_parametrees = [
        position for position, chemin in enumerate(chemins) if chemin.startswith(PREFIXE_PARAMETRE)
    ]

    assert positions_parametrees
    assert chemins.index(CHEMIN_A_VALIDER) < min(positions_parametrees)
