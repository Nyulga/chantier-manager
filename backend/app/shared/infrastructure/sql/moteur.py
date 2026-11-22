"""Création du moteur SQLAlchemy et de l'usine de sessions."""

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import ConnectionPoolEntry


def _activer_cles_etrangeres(
    connexion: DBAPIConnection, _enregistrement: ConnectionPoolEntry
) -> None:
    """Active les clés étrangères de SQLite, qu'il ignore par défaut.

    Sans cela, une étape pourrait référencer un chantier inexistant en SQLite alors
    que PostgreSQL le refuserait : les deux bases doivent se comporter pareil.
    """
    curseur = connexion.cursor()
    curseur.execute("PRAGMA foreign_keys=ON")
    curseur.close()


def creer_moteur(url_base: str) -> Engine:
    """Crée le moteur synchrone de la base désignée par l'URL (ADR 0002).

    La connexion n'est ouverte qu'à la première requête : créer un moteur ne touche
    pas la base.
    """
    moteur = create_engine(url_base)
    if moteur.dialect.name == "sqlite":
        event.listen(moteur, "connect", _activer_cles_etrangeres)
    return moteur


def creer_usine_sessions(moteur: Engine) -> sessionmaker[Session]:
    """Crée l'usine de sessions des Unit of Work.

    `expire_on_commit=False` : après la validation, les objets restent lisibles,
    car les cas d'usage construisent leur vue avant de sortir de la transaction.
    """
    return sessionmaker(bind=moteur, expire_on_commit=False)
