"""Schémas de réponse des routes du noyau partagé."""

from typing import Literal

from pydantic import BaseModel, ConfigDict


class ReponseSante(BaseModel):
    """Réponse de la route de santé : indique que l'API répond.

    Le seul statut possible est « ok » : si l'API ne répond pas, il n'y a pas de
    réponse du tout. Le type littéral le fait apparaître tel quel dans le schéma
    OpenAPI, donc dans le client TypeScript généré.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    statut: Literal["ok"]
