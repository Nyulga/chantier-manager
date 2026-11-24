"""Cas d'usage : créer un chantier."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from app.chantiers.application.plafonds import LIMITE_CHANTIERS, MESSAGE_LIMITE_CHANTIERS
from app.chantiers.application.ports import RESUME_SANS_ETAPE, UnitOfWorkChantiers
from app.chantiers.application.vues import ChantierVue, vue_chantier
from app.chantiers.domain.adresse import Adresse
from app.chantiers.domain.chantier import Chantier, FicheChantier
from app.chantiers.domain.montant import Montant
from app.chantiers.domain.politiques import peut_creer_chantier
from app.shared.application.acces import exiger_acces
from app.shared.application.plafond import exiger_place_sous_le_plafond
from app.shared.application.ports import GenerateurId, Horloge
from app.shared.domain.acteur import Acteur


@dataclass(frozen=True)
class NouveauChantier:
    """Commande de création d'un chantier, avec des valeurs simples ; le budget est en euros."""

    nom: str
    voie: str
    code_postal: str
    ville: str
    client: str
    date_debut: date
    echeance: date
    budget: Decimal


class CreerChantier:
    """Crée un chantier, ce que seul un chef peut faire.

    Un chantier qui vient d'être créé n'a encore aucune étape : son résumé est nul
    (0 % et aucun compteur), sans qu'il soit besoin de le demander au module étapes.
    L'horloge sert au délai de la vue : une échéance déjà passée est acceptée, et le
    chantier apparaît alors aussitôt en retard.

    Le plafond de la démo (`LIMITE_CHANTIERS`) est vérifié après le droit : un ouvrier
    reçoit toujours son refus de droit, et n'apprend rien du nombre de chantiers. Il
    l'est aussi après la validation de la saisie, qui ne lit rien, et dans la même
    transaction que l'ajout, avant toute écriture : un refus n'enregistre rien.

    Lève :
        AccesRefuseError : l'acteur n'est pas chef.
        ValeurInvalideError : une information du chantier viole un invariant du domaine.
        PlafondAtteintError : la démo compte déjà `LIMITE_CHANTIERS` chantiers.
    """

    def __init__(
        self, uow: UnitOfWorkChantiers, generateur_id: GenerateurId, horloge: Horloge
    ) -> None:
        self._uow = uow
        self._generateur_id = generateur_id
        self._horloge = horloge

    def executer(self, commande: NouveauChantier, acteur: Acteur) -> ChantierVue:
        """Crée le chantier et renvoie sa vue pour l'acteur."""
        # AccesRefuseError, et non NonTrouveError : il n'y a ici aucun chantier existant à cacher.
        exiger_acces(
            autorise=peut_creer_chantier(acteur), message="Seul un chef peut créer un chantier."
        )
        fiche = FicheChantier(
            nom=commande.nom,
            adresse=Adresse(commande.voie, commande.code_postal, commande.ville),
            client=commande.client,
            date_debut=commande.date_debut,
            echeance=commande.echeance,
            budget=Montant(commande.budget),
        )
        with self._uow:
            # Le nombre de chantiers vient de la liste complète : c'est acceptable tant que
            # ce même plafond la borne à 100 chantiers. Si le plafond montait, un comptage
            # par la base serait à ajouter au port, avec ses implémentations (`dev-donnees`).
            existants = len(self._uow.chantiers.lister())
            exiger_place_sous_le_plafond(existants, LIMITE_CHANTIERS, MESSAGE_LIMITE_CHANTIERS)
            chantier = Chantier.creer(self._generateur_id.nouveau(), fiche)
            self._uow.chantiers.ajouter(chantier)
            self._uow.valider()
        aujourd_hui = self._horloge.aujourd_hui()
        return vue_chantier(chantier, acteur, RESUME_SANS_ETAPE, aujourd_hui)
