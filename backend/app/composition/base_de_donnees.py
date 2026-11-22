"""Base de données de l'application : moteur, sessions et migrations au démarrage."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from sqlalchemy.orm import Session, sessionmaker

from app.shared.infrastructure.sql.moteur import creer_moteur, creer_usine_sessions

RACINE_BACKEND = Path(__file__).resolve().parents[2]


def configuration_alembic(url_base: str) -> Config:
    """Construit la configuration Alembic pour la base désignée par l'URL.

    L'URL passe par `attributes` plutôt que par `set_main_option` : le fichier .ini
    est lu par `configparser`, qui interprète les « % » d'une URL.
    """
    configuration = Config(str(RACINE_BACKEND / "alembic.ini"))
    configuration.attributes["url_base"] = url_base
    return configuration


class BaseDeDonnees:
    """Moteur et sessions d'une application, créés une seule fois au lancement."""

    def __init__(self, url_base: str) -> None:
        self._url_base = url_base
        self._moteur = creer_moteur(url_base)
        self.usine_sessions: sessionmaker[Session] = creer_usine_sessions(self._moteur)

    @asynccontextmanager
    async def cycle_de_vie(self, _application: FastAPI) -> AsyncIterator[None]:
        """Applique les migrations au démarrage, et libère les connexions à l'arrêt.

        En production, la base SQLite est ainsi créée dans le volume au premier
        lancement, puis mise à jour à chaque nouvelle version, sans geste manuel.
        """
        command.upgrade(configuration_alembic(self._url_base), "head")
        yield
        self._moteur.dispose()
