"""Types de colonnes communs aux modules."""

from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import DateTime, Dialect, Enum
from sqlalchemy.types import TypeDecorator


class DateHeureUtc(TypeDecorator[datetime]):
    """Date et heure toujours relues en UTC, avec leur fuseau.

    SQLite ne conserve pas le fuseau et renverrait des dates « naïves », que le
    domaine ne saurait pas comparer à `Horloge.maintenant()`. On n'enregistre donc
    que des dates avec fuseau, converties en UTC, et on rend le fuseau à la lecture.
    """

    impl = DateTime(timezone=True)
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        """Refuse une date sans fuseau, puis la convertit en UTC."""
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("Une date enregistrée doit porter son fuseau horaire.")
        return value.astimezone(UTC)

    def process_result_value(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        """Rend le fuseau UTC aux dates relues sans fuseau."""
        if value is None or value.tzinfo is not None:
            return value
        return value.replace(tzinfo=UTC)


def enum_texte(classe: type[StrEnum], nom: str) -> Enum:
    """Colonne texte qui ne contient que les valeurs de l'énumération.

    Le type est un texte (`native_enum=False`) plutôt qu'un `ENUM` natif de
    PostgreSQL : ajouter une valeur ne demande alors qu'une migration de contrainte.
    Une contrainte CHECK nommée protège la base (règle 07). On enregistre la valeur
    (`"en_cours"`), pas le nom du membre, pour relire de vrais membres d'énumération.
    """
    return Enum(
        classe,
        name=nom,
        native_enum=False,
        create_constraint=True,
        values_callable=lambda membres: [membre.value for membre in membres],
    )
