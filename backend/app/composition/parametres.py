"""Paramètres de l'application, lus une seule fois (règle 06)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Parametres(BaseSettings):
    """Configuration issue des variables d'environnement `CHANTIER_*`.

    La valeur par défaut convient au développement local : une base SQLite dans
    le dossier courant. En production, `CHANTIER_URL_BASE` pointe vers le volume.
    Seule la composition root lit cette configuration, puis la transmet en paramètre.
    """

    model_config = SettingsConfigDict(env_prefix="CHANTIER_")

    url_base: str = "sqlite:///./chantier.db"
