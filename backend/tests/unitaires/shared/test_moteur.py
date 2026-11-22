"""Moteur SQLAlchemy : le réglage propre à SQLite n'est pas appliqué aux autres bases."""

from sqlalchemy import event

from app.shared.infrastructure.sql.moteur import _activer_cles_etrangeres, creer_moteur

# Un port fermé : le test prouve que créer le moteur ne tente aucune connexion.
URL_POSTGRESQL_INJOIGNABLE = "postgresql+psycopg://demo:demo@127.0.0.1:1/chantiers"


def test_un_moteur_postgresql_est_cree_sans_connexion_ni_reglage_propre_a_sqlite() -> None:
    moteur = creer_moteur(URL_POSTGRESQL_INJOIGNABLE)

    assert moteur.dialect.name == "postgresql"
    assert not event.contains(moteur, "connect", _activer_cles_etrangeres)
