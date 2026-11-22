"""Configuration partagée des tests : profil hypothesis et base SQLite jetable."""

import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from hypothesis import settings
from sqlalchemy.orm import Session, sessionmaker

from app.composition.mapping import metadonnees
from app.shared.infrastructure.sql.moteur import creer_moteur, creer_usine_sessions

# En CI, hypothesis tire ses exemples de façon déterministe (`derandomize`) : un
# échec se reproduit à l'identique d'une exécution à l'autre, et la CI ne devient
# jamais rouge au hasard d'un tirage (règle 07, tests déterministes). Aucune base
# d'exemples n'est gardée, puisque l'environnement de CI est jetable. En local, le
# tirage reste aléatoire, pour explorer d'autres cas à chaque lancement.
# Hypothesis charge déjà un profil semblable quand il reconnaît une CI ; on le
# déclare ici pour ne pas dépendre de cette détection interne. La variable `CI`
# est celle que définit GitHub Actions ; ce n'est pas une configuration de l'application.
settings.register_profile("ci", derandomize=True, database=None)
if "CI" in os.environ:
    settings.load_profile("ci")


def url_sqlite(dossier: Path) -> str:
    """Construit l'URL d'une base SQLite placée dans le dossier temporaire d'un test."""
    return f"sqlite:///{dossier / 'test.db'}"


@pytest.fixture
def usine_sessions(tmp_path: Path) -> Iterator[sessionmaker[Session]]:
    """Fournit une usine de sessions sur une base SQLite vide, dont le schéma est créé.

    Le schéma vient directement des mappings (`create_all`) : c'est le test des
    migrations qui prouve que les migrations produisent le même schéma.
    """
    moteur = creer_moteur(url_sqlite(tmp_path))
    metadonnees().create_all(moteur)
    yield creer_usine_sessions(moteur)
    moteur.dispose()
