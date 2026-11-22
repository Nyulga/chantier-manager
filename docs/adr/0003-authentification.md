# ADR 0003 : authentification, sessions et invitations

- **Statut** : accepté
- **Date** : 2026-11-22

## Contexte

- Le niveau de sécurité attendu est OWASP ASVS niveau 2.
- Les clients sont le web aujourd'hui et le mobile demain, avec la même API.
- Il n'y a pas d'inscription publique : les comptes sont créés par invitation.
- Seuls les e-mails de sécurité font partie de la V1 : invitation et réinitialisation du mot de passe.

## Décision

**Mots de passe**
- Hachés en Argon2id (argon2-cffi), via le port `HacheurMotDePasse`.
- Politique : 12 caractères minimum, et refus des mots de passe présents dans une liste locale de mots de passe courants ou fuités.

**Sessions**
- Token d'accès : **JWT de 15 minutes** (PyJWT), avec un algorithme fixé côté serveur et des claims `exp`, `iat`, `sub` et `sid` vérifiés.
- Refresh token :
  - token **opaque** et aléatoire, **stocké haché** en base ;
  - **rotation** à chaque utilisation ;
  - **détection de réutilisation** : la présentation d'un refresh token déjà utilisé révoque toute la session.
- Déconnexion : révocation de la session côté serveur.

**Transport**
- Web : cookies `HttpOnly`, `Secure` et `SameSite=Strict`, avec un token CSRF en *double submit* sur toutes les méthodes qui modifient des données.
- Le front et l'API sont sur la **même origine**, donc aucun CORS.
- Mobile (plus tard) : même mécanisme, mais avec un en-tête `Authorization: Bearer`.

**Limitation des tentatives** : par IP et par compte, avec un blocage temporaire progressif. Elle passe par un port, avec une implémentation en base pour la V1.

**Invitations et réinitialisations**
- Token aléatoire de 256 bits, **à usage unique**, **stocké haché**, avec une durée de vie courte (invitation : 72 h ; réinitialisation : 30 min).
- Envoi par le port `EnvoiEmail` : SMTP d'un fournisseur établi dans l'UE en production, Mailpit en développement.
- La demande de réinitialisation renvoie toujours la même réponse, pour ne pas révéler quels comptes existent.

**Premier compte** : commande CLI `creer-premier-chef`, exécutée sur le serveur.

## Alternatives écartées

| Option | Raison du rejet |
|---|---|
| **JWT longs dans le `localStorage`** | Exposés au XSS et impossibles à révoquer. |
| **Refresh token en JWT** | Révocation et détection de réutilisation plus difficiles qu'avec un token opaque en base. |
| **Sessions serveur uniquement (cookie de session)** | Conviendrait au web, mais moins naturel pour le futur mobile. Le modèle retenu couvre les deux. |
| **Fournisseur d'identité externe (Keycloak, Auth0…)** | Surdimensionné, et introduit un tiers pour les données personnelles. |
| **fastapi-users** | Ne colle pas à l'architecture hexagonale, et la rotation avec détection de réutilisation n'est pas fournie en natif. |

## Conséquences

- Il faut une table des sessions et des refresh tokens, purgée régulièrement.
- Le CSRF doit être géré par le frontend : il lit le cookie CSRF et le renvoie dans un en-tête.
- Chaque règle (expiration, réutilisation, limitation des tentatives) a ses tests d'intégration.
