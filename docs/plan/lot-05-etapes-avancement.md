# Lot 05 – Étapes et avancement

**Dépend de** : 04 · **Statut** : à faire

## Objectif
Le cœur métier : des étapes qui suivent un cycle de validation contrôlé, avec leur historique, et l'avancement calculé du chantier.

## Contenu
- **Domaine** :
  - `Etape` : titre, description, ordre, statut ;
  - **machine à états** avec une table explicite des transitions par rôle :
    - ouvrier ou chef rattaché : `À faire` → `En cours` → `Terminée (à valider)` ;
    - chef du chantier : `Terminée (à valider)` → `Validée`, ou → `En cours` (refus, avec un commentaire obligatoire) ;
  - toute autre transition lève `TransitionInterdite` ;
  - `HistoriqueEtape` (auteur, ancien statut, nouveau statut, date, commentaire) ;
  - calcul de l'`Avancement`.
- **Cas d'usage** : ajouter, modifier, réordonner et supprimer une étape (chef) ; démarrer, signaler terminée, valider, refuser ; consulter l'historique.
- **Atomicité** : la transition et l'écriture de l'historique se font dans le même Unit of Work.
- **Tests** :
  - **par propriétés** (hypothesis) : aucune suite d'actions ne permet d'atteindre `Validée` sans passer par un chef ; l'avancement reste toujours entre 0 et 100 % ;
  - de mutation sur la machine à états.
- **Frontend** : liste des étapes avec leur statut, actions selon le rôle, historique, barre d'avancement sur la liste et sur le détail du chantier.
- **Tests e2e** : l'ouvrier signale une étape terminée → le chef la refuse avec un commentaire → l'ouvrier la signale de nouveau → le chef la valide → l'avancement est mis à jour.

## Critères d'acceptation
- [ ] Tous les critères « Étapes et avancement » d'`intent.md` §5.1.
- [ ] 100 % de couverture et au moins 90 % de score de mutation sur la machine à états et le calcul de l'avancement.

## Hors lot
Planning et dates par étape, notifications.
