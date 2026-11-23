"""Erreurs de validation de pydantic, converties en erreurs par champ et en français.

Le détail natif de FastAPI est en anglais et recopie la valeur envoyée, qui peut
être une donnée personnelle : on n'en garde que le chemin du champ et le type de
l'erreur, dont on tire un message écrit à la main.
"""

from collections.abc import Mapping, Sequence
from typing import Any

from fastapi.exceptions import RequestValidationError

from app.shared.api.schemas import ErreurChampReponse

MESSAGE_PAR_DEFAUT = "La valeur n'est pas valide."
NOMBRE_ENTIER = "Ce champ doit être un nombre entier."
MONTANT = "Ce champ doit être un montant valide."
DATE = "Ce champ doit être une date valide."
IDENTIFIANT = "Ce champ doit être un identifiant valide."
VALEUR_NON_PERMISE = "Cette valeur n'est pas permise."

# Message de chaque type d'erreur de pydantic. Les accolades sont remplies avec le
# contexte de l'erreur (`max_length`, `ge`…), qui ne contient que des bornes.
MESSAGE_PAR_TYPE: Mapping[str, str] = {
    "missing": "Ce champ est obligatoire.",
    "extra_forbidden": "Ce champ n'est pas attendu.",
    "string_type": "Ce champ doit être un texte.",
    "string_too_long": "Ce champ ne doit pas dépasser {max_length} caractères.",
    "string_too_short": "Ce champ doit contenir au moins {min_length} caractères.",
    "int_type": NOMBRE_ENTIER,
    "int_parsing": NOMBRE_ENTIER,
    "int_from_float": NOMBRE_ENTIER,
    "decimal_type": MONTANT,
    "decimal_parsing": MONTANT,
    "date_type": DATE,
    "date_parsing": DATE,
    "date_from_datetime_parsing": DATE,
    "uuid_type": IDENTIFIANT,
    "uuid_parsing": IDENTIFIANT,
    "literal_error": VALEUR_NON_PERMISE,
    "enum": VALEUR_NON_PERMISE,
    "greater_than_equal": "Ce champ doit être supérieur ou égal à {ge}.",
    "greater_than": "Ce champ doit être strictement supérieur à {gt}.",
    "less_than_equal": "Ce champ doit être inférieur ou égal à {le}.",
    "less_than": "Ce champ doit être strictement inférieur à {lt}.",
}


def concerne_le_chemin(erreur: RequestValidationError) -> bool:
    """Dit si l'une des erreurs porte sur un paramètre du chemin (`/chantiers/{id}`).

    Le premier élément de l'emplacement d'une erreur nomme sa provenance : `body`,
    `query`, `path`, `header`.
    """
    return any(detail["loc"][:1] == ("path",) for detail in erreur.errors())


def erreurs_par_champ(erreur: RequestValidationError) -> list[ErreurChampReponse]:
    """Liste les erreurs qui désignent un champ, avec leur message en français.

    Une erreur qui ne désigne aucun champ est omise : c'est le cas d'un corps qui
    n'est pas du JSON, dont l'emplacement n'est qu'une position dans le texte. La
    réponse garde alors son `detail` global.
    """
    erreurs = []
    for detail in erreur.errors():
        champ = _chemin(detail["loc"])
        if champ:
            erreurs.append(ErreurChampReponse(champ=champ, message=_message(detail)))
    return erreurs


def _chemin(emplacement: Sequence[int | str]) -> str:
    """Écrit le chemin d'un champ (`adresse.code_postal`), sans la provenance de tête."""
    parties = emplacement[1:]
    if not any(isinstance(partie, str) for partie in parties):
        return ""
    return ".".join(str(partie) for partie in parties)


def _message(detail: Mapping[str, Any]) -> str:
    """Choisit le message du type d'erreur, et y insère les bornes de son contexte."""
    modele = MESSAGE_PAR_TYPE.get(detail["type"], MESSAGE_PAR_DEFAUT)
    return modele.format_map(detail.get("ctx") or {})
