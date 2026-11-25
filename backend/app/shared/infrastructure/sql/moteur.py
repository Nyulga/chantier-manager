"""Création du moteur SQLAlchemy et de l'usine de sessions."""

from sqlalchemy import Connection, Engine, create_engine, event
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import ConnectionPoolEntry


def _activer_cles_etrangeres(
    connexion: DBAPIConnection, _enregistrement: ConnectionPoolEntry
) -> None:
    """Active les clés étrangères de SQLite, qu'il ignore par défaut.

    Sans cela, une ligne pourrait référencer une ligne inexistante d'une autre table
    en SQLite, alors que PostgreSQL le refuserait : les deux bases doivent se
    comporter pareil.
    """
    curseur = connexion.cursor()
    curseur.execute("PRAGMA foreign_keys=ON")
    curseur.close()


def _commencer_en_ecriture(connexion: Connection) -> None:
    """Ouvre chaque transaction par `BEGIN IMMEDIATE`, qui prend aussitôt le verrou d'écriture.

    Les plafonds de la démo (ADR 0016) sont vérifiés par lecture puis comptage, dans la
    transaction qui écrit ensuite. Avec le `BEGIN` différé de SQLite, le verrou
    d'écriture n'est pris qu'à la première écriture : plusieurs créations simultanées
    liraient toutes « 99 chantiers » avant d'écrire, et le plafond serait dépassé.
    Avec `IMMEDIATE`, la lecture du comptage et l'écriture se font sous le même verrou :
    les créations passent l'une après l'autre. Une transaction qui attend le verrou
    patiente jusqu'au délai du pilote (5 secondes par défaut) ; au-delà, SQLite lève
    « database is locked », que l'Unit of Work traduit en `ServiceIndisponibleError`
    (503, ADR 0008).

    L'Unit of Work ne distingue pas lecture et écriture : toutes les transactions sont
    donc immédiates et passent l'une après l'autre. C'est acceptable pour la démo, qui
    n'a qu'un seul processus API (ADR 0016) et des transactions très courtes.

    Méthode décrite par la documentation de SQLAlchemy (dialecte SQLite, « Transactions
    with SQLite and the sqlite3 driver ») : `isolation_level=None` côté pilote, puis
    `BEGIN` émis à l'événement `begin`. Elle est propre à SQLite : au retour de
    PostgreSQL (ADR 0007), il faudra la réserver à ce dialecte.
    """
    connexion.exec_driver_sql("BEGIN IMMEDIATE")


def creer_moteur(url_base: str) -> Engine:
    """Crée le moteur synchrone de la base désignée par l'URL (ADR 0002).

    La connexion n'est ouverte qu'à la première requête : créer un moteur ne touche
    pas la base. Le réglage des clés étrangères est propre à SQLite, la seule base
    prise en charge pendant le squelette (ADR 0007) : au retour de PostgreSQL, il
    faudra le réserver à SQLite (`moteur.dialect.name == "sqlite"`), car PostgreSQL
    ne comprend pas `PRAGMA`.

    `hide_parameters=True` : les messages d'erreur de SQLAlchemy citent d'ordinaire les
    valeurs de la requête, donc des données personnelles. Elles se retrouveraient dans
    le journal du serveur à la moindre erreur d'intégrité (intent.md, §3.2).
    """
    # `isolation_level=None` : `sqlite3` n'émet plus aucun `BEGIN` ; c'est l'événement `begin`
    # ci-dessous qui ouvre les transactions (voir `_commencer_en_ecriture`).
    moteur = create_engine(url_base, hide_parameters=True, connect_args={"isolation_level": None})
    event.listen(moteur, "connect", _activer_cles_etrangeres)
    event.listen(moteur, "begin", _commencer_en_ecriture)
    return moteur


def creer_usine_sessions(moteur: Engine) -> sessionmaker[Session]:
    """Crée l'usine de sessions des Unit of Work.

    `expire_on_commit=False` : après la validation, les objets restent lisibles.
    Plusieurs cas d'usage construisent en effet leur vue après être sortis de la
    transaction, une fois la session fermée. Sans cette option, la validation
    expirerait les attributs des objets, et les relire sur une session fermée
    lèverait une erreur.
    """
    return sessionmaker(bind=moteur, expire_on_commit=False)
