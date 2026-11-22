"""Fixtures partagées : une base SQLite jetable, avec le schéma des mappings."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy.orm import Session, sessionmaker

from app.composition.mapping import metadonnees
from app.shared.infrastructure.sql.moteur import creer_moteur, creer_usine_sessions


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
