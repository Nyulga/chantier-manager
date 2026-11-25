"""Erreurs de validation de pydantic, converties en erreurs par champ et en français.

Le détail natif de FastAPI est en anglais et recopie la valeur envoyée, qui peut
être une donnée personnelle : on n'en garde que le chemin du champ et le type de
l'erreur, dont on tire un message écrit à la main.
"""

import re
from collections.abc import Mapping
from typing import Any

from fastapi.exceptions import RequestValidationError

from app.shared.api.schemas import ErreurChampReponse

MESSAGE_PAR_DEFAUT = "La valeur n'est pas valide."
NOMBRE_ENTIER = "Ce champ doit être un nombre entier."
MONTANT = "Ce champ doit être un montant valide."
DATE = "Ce champ doit être une date valide."
IDENTIFIANT = "Ce champ doit être un identifiant valide."
VALEUR_NON_PERMISE = "Cette valeur n'est pas permise."
# Type d'erreur de pydantic pour une clé que le schéma n'attend pas (`extra="forbid"`).
CLE_EN_TROP = "extra_forbidden"
# Forme d'un nom de champ : lettres ASCII, chiffres et `_`, 64 caractères au plus. Une clé en
# trop n'est nommée dans la réponse que si elle a cette forme : une saisie libre (une adresse
# e-mail, un texte) n'y ressemble pas et ne doit jamais être recopiée (voir `_chemin`).
FORME_NOM_DE_CHAMP = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,63}")

# Message de chaque type d'erreur de pydantic. Les accolades sont remplies avec le
# contexte de l'erreur (`max_length`, `ge`…), qui ne contient que des bornes.
MESSAGE_PAR_TYPE: Mapping[str, str] = {
    "missing": "Ce champ est obligatoire.",
    CLE_EN_TROP: "Ce champ n'est pas attendu.",
    "string_type": "Ce champ doit être un texte.",
    "string_too_long": "Ce champ ne doit pas dépasser {max_length} caractères.",
    "string_too_short": "Ce champ doit contenir au moins {min_length} caractères.",
    "int_type": NOMBRE_ENTIER,
    "int_parsing": NOMBRE_ENTIER,
    "int_from_float": NOMBRE_ENTIER,
    "decimal_type": MONTANT,
    "decimal_parsing": MONTANT,
    "decimal_max_digits": "Ce montant a trop de chiffres.",
    "decimal_whole_digits": "Ce montant est trop élevé.",
    "decimal_max_places": "Ce montant ne doit pas avoir plus de {decimal_places} décimales.",
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
    """Dit si l'une des erreurs porte sur un paramètre du chemin de l'URL.

    Le premier élément de l'emplacement d'une erreur nomme sa provenance : `body`,
    `query`, `path`, `header`.
    """
    return any(detail["loc"][:1] == ("path",) for detail in erreur.errors())


def erreurs_par_champ(erreur: RequestValidationError) -> list[ErreurChampReponse]:
    """Liste les erreurs qui désignent un champ, avec leur message en français.

    Une erreur qui ne désigne aucun champ est omise : c'est le cas d'un corps qui
    n'est pas du JSON, dont l'emplacement n'est qu'une position dans le texte. La
    réponse garde alors son `detail` global. Une clé en trop qui n'a pas la forme d'un
    nom de champ est listée avec le chemin de l'objet qui la contient (vide à la racine).
    """
    erreurs = []
    for detail in erreur.errors():
        champ = _chemin(detail)
        if champ is not None:
            erreurs.append(ErreurChampReponse(champ=champ, message=_message(detail)))
    return erreurs


def _chemin(detail: Mapping[str, Any]) -> str | None:
    """Écrit le chemin d'un champ (`adresse.code_postal`), sans la provenance de tête.

    Renvoie `None` quand l'emplacement ne désigne aucun champ. Pour une clé en trop,
    l'emplacement se termine par la clé inventée par le client : elle peut être
    n'importe quel texte, une adresse e-mail par exemple. Elle n'est recopiée dans le
    chemin que si elle a la forme d'un nom de champ (`FORME_NOM_DE_CHAMP`), ce qui aide
    le client à corriger une faute de frappe. Sinon on désigne l'objet qui la contient,
    le chemin vide étant la racine du corps.
    """
    parties = detail["loc"][1:]
    if not any(isinstance(partie, str) for partie in parties):
        return None
    if detail["type"] == CLE_EN_TROP and not FORME_NOM_DE_CHAMP.fullmatch(str(parties[-1])):
        parties = parties[:-1]
    return ".".join(str(partie) for partie in parties)


def _message(detail: Mapping[str, Any]) -> str:
    """Choisit le message du type d'erreur, et y insère les bornes de son contexte."""
    modele = MESSAGE_PAR_TYPE.get(detail["type"], MESSAGE_PAR_DEFAUT)
    return modele.format_map(detail.get("ctx") or {})
