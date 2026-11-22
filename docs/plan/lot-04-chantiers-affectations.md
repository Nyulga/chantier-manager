# Lot 04 – Chantiers et affectations

**Dépend de** : 03 · **Statut** : à faire

## Objectif
Gérer les chantiers et leurs affectations, avec un cloisonnement strict pour les chefs comme pour les ouvriers.

## Contenu
- **Domaine** :
  - agrégat `Chantier` ;
  - objets valeur `Adresse` et `Montant` (`Decimal`, EUR) ;
  - invariants : l'échéance n'est pas avant la date de début ; un chantier a toujours au moins un chef ; un chantier archivé est en lecture seule.
- **Politiques d'accès** : `peut_voir`, `peut_modifier`, `peut_voir_budget`, `peut_affecter`, et une **matrice de tests exhaustive** rôle × action × rattachement × statut du chantier.
- **Service public** pour les autres modules : `est_rattache(utilisateur, chantier)`, `est_chef_du_chantier(utilisateur, chantier)`.
- **Cas d'usage** : créer (le créateur devient chef du chantier), modifier, archiver, lister « mes chantiers », consulter le détail, affecter ou retirer un chef ou un ouvrier.
- **API** :
  - 404 pour tout chantier hors du périmètre de l'utilisateur ;
  - le budget est absent des réponses envoyées aux ouvriers (deux schémas de réponse distincts).
- **Frontend** : liste de mes chantiers (avancement à 0 % tant que le lot 05 n'est pas fait, échéance), formulaire de création et de modification, détail du chantier, gestion de l'équipe.
- **Tests e2e** : un chef crée un chantier et affecte un ouvrier ; l'ouvrier voit le chantier sans le budget ; un second chef ne le voit pas.

## Critères d'acceptation
- [ ] Tous les critères « Chantiers et cloisonnement » d'`intent.md` §5.1.
- [ ] La matrice d'accès est couverte à 100 %, et le score de mutation des politiques est d'au moins 90 %.

## Hors lot
Planning, rôles client et sous-traitant, devis.
