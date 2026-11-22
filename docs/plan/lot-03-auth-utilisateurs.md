# Lot 03 – Auth et utilisateurs

**Dépend de** : 02 · **Statut** : à faire · **Référence** : [ADR 0003](../adr/0003-authentification.md)

## Objectif
Des comptes sécurisés : premier chef créé en CLI, invitations, connexion, sessions avec rotation, et mot de passe oublié.

## Contenu
- **Domaine** : `Utilisateur` (e-mail, nom, rôle `CHEF` ou `OUVRIER`, actif), objet valeur `Email`, politique de mot de passe, `Session` et `RefreshToken` (avec leur famille, pour la détection de réutilisation), `Invitation` et `JetonReinitialisation`.
- **Ports** : `UtilisateurRepository`, `SessionRepository`, `InvitationRepository`, `HacheurMotDePasse` (Argon2id), `EnvoiEmail` (SMTP en production, Mailpit en développement, mémoire en test), `LimiteurTentatives`.
- **Cas d'usage** : se connecter, rafraîchir la session, se déconnecter, inviter (réservé aux chefs), accepter une invitation, demander une réinitialisation, réinitialiser le mot de passe, consulter son profil.
- **CLI** : `creer-premier-chef`, qui refuse de s'exécuter si un chef existe déjà.
- **Liste locale** de mots de passe courants ou fuités, embarquée dans le projet.
- **Frontend** : pages de connexion, d'acceptation d'invitation, de mot de passe oublié et de réinitialisation, et page « Inviter un utilisateur » pour les chefs ; garde de routes ; gestion du CSRF et du rafraîchissement automatique de la session.
- **Tests e2e** : création du premier chef → invitation d'un ouvrier (lien récupéré dans Mailpit) → connexion de l'ouvrier.

## Critères d'acceptation
- [ ] Tous les critères « Comptes et accès » d'`intent.md` §5.1.
- [ ] La limitation des tentatives de connexion est vérifiée par un test (§5.3).
- [ ] Un JWT expiré, falsifié, ou signé avec un autre algorithme est refusé.
- [ ] Les tokens d'invitation, de réinitialisation et de refresh sont stockés **hachés**, ce que vérifie un test sur la base.

## Hors lot
Rôles supplémentaires, inscription publique, authentification à deux facteurs.
