"""Cas d'usage : lister les étapes d'un chantier, dans leur ordre."""

from uuid import UUID

from app.etapes.application.ports import UnitOfWorkEtapes, VerificationChantier
from app.etapes.application.vues import EtapeVue, vue_etape
from app.shared.domain.acteur import Acteur


class ListerEtapes:
    """Liste les étapes d'un chantier, chacune avec les actions permises à l'acteur.

    L'existence du chantier est vérifiée d'abord : un chantier inconnu doit donner
    une erreur (404), et non une liste vide qui laisserait croire qu'il existe.
    Dans le squelette, chef et ouvrier voient les étapes de tous les chantiers.

    Lève :
        NonTrouveError : le chantier n'existe pas.
    """

    def __init__(self, uow: UnitOfWorkEtapes, verification: VerificationChantier) -> None:
        self._uow = uow
        self._verification = verification

    def executer(self, chantier_id: UUID, acteur: Acteur) -> tuple[EtapeVue, ...]:
        """Renvoie la vue de chaque étape du chantier, triées par ordre."""
        self._verification.executer(chantier_id)
        with self._uow:
            etapes = self._uow.etapes.lister_par_chantiers([chantier_id])
            return tuple(vue_etape(etape, acteur) for etape in etapes)
