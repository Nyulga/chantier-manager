"""Les `Literal` des schémas d'API et les énumérations du domaine ont les mêmes valeurs.

L'api n'importe pas le domaine : elle répète les statuts et les actions en `Literal`,
qui typent le client TypeScript généré. Ce test échoue dès qu'une valeur est ajoutée,
retirée ou renommée d'un seul côté.
"""

from typing import get_args

from app.etapes.api import schemas
from app.etapes.domain import cycle


def test_les_statuts_exposes_par_l_api_sont_ceux_du_domaine() -> None:
    assert set(get_args(schemas.StatutReponse)) == {statut.value for statut in cycle.StatutEtape}


def test_les_actions_exposees_par_l_api_sont_celles_du_domaine() -> None:
    assert set(get_args(schemas.ActionEtape)) == {action.value for action in cycle.ActionEtape}
