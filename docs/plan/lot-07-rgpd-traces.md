# Lot 07 – RGPD et traces

**Dépend de** : 03, 04, 05, 06 · **Statut** : à faire

## Objectif
Respecter les droits des personnes et les durées de conservation, et tracer les actions sensibles.

## Contenu
- **Journal des actions sensibles** : connexion, échec de connexion, invitation, changement de mot de passe, validation ou refus d'une étape, suppression. Il est conservé en base et ne contient aucune donnée sensible. Les autres modules l'alimentent via un port `JournalAudit`.
- **Droit d'accès et à la portabilité** : export JSON des données personnelles de l'utilisateur (profil, notes, fichiers envoyés : liste et métadonnées).
- **Droit à l'effacement** : suppression du compte, avec anonymisation des contributions qui doivent rester sur les chantiers (notes et historique attribués à « Utilisateur supprimé »).
- **Durées de conservation** (valeurs à confirmer au début du lot) : chantiers archivés, journal, sessions expirées, invitations expirées. CLI `purger` lancée par un timer systemd.
- **Pages légales** : politique de confidentialité et mentions légales, accessibles sans être connecté.
- **Registre des traitements** : `docs/rgpd/registre-des-traitements.md`.
- **Frontend** : page « Mes données » (export, suppression avec confirmation).

## Critères d'acceptation
- [ ] Tous les critères « RGPD » d'`intent.md` §5.1.
- [ ] Après la suppression d'un compte, aucune donnée personnelle de l'utilisateur ne subsiste en base (test).

## Hors lot
Gestion des consentements marketing (aucun traitement de ce type dans le projet).
