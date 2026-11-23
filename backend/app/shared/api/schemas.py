"""Schémas communs des routes : réponse de santé, corps d'erreur et configuration des DTO."""

from typing import Literal

from pydantic import BaseModel, ConfigDict

# Les espaces autour d'une saisie sont retirés dès l'api : le domaine ne le fait pas.
CONFIG_ENTREE = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)
CONFIG_SORTIE = ConfigDict(extra="forbid", frozen=True)


class ReponseSante(BaseModel):
    """Réponse de la route de santé : indique que l'API répond.

    Le seul statut possible est « ok » : si l'API ne répond pas, il n'y a pas de
    réponse du tout. Le type littéral le fait apparaître tel quel dans le schéma
    OpenAPI, donc dans le client TypeScript généré.
    """

    model_config = CONFIG_SORTIE

    statut: Literal["ok"]


class ProblemeReponse(BaseModel):
    """Corps de toute réponse d'erreur, au format « problem details » (RFC 9457).

    `title` est le libellé court du statut et `detail` le message à afficher, en
    français, sans aucun détail interne. Le type est toujours `about:blank` : le
    statut HTTP dit déjà tout ce que le client a besoin de savoir.
    """

    model_config = CONFIG_SORTIE

    type: str
    title: str
    status: int
    detail: str


class ErreurChampReponse(BaseModel):
    """Une erreur de saisie attachée à un champ, que l'écran affiche sous ce champ.

    `champ` est le chemin du champ dans le corps de la requête (`nom`, `adresse.voie`),
    ou le nom du paramètre de requête (`limite`). `message` est une phrase en français.
    """

    model_config = CONFIG_SORTIE

    champ: str
    message: str


class ProblemeValidationReponse(ProblemeReponse):
    """Réponse 422 : le problème, et la liste des champs en cause.

    `erreurs` est vide quand l'erreur ne porte pas sur un champ précis, par exemple
    une échéance qui précède le début ; seul `detail` la décrit alors.
    """

    erreurs: list[ErreurChampReponse]
