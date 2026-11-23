# Lot 03 – Auth et utilisateurs

**Dépend de** : 02 · **Statut** : à faire · **Issue** : #3 · **Référence** : [ADR 0003](../adr/0003-authentification.md)

## Objectif
Des comptes sécurisés : le premier chef créé en CLI, les invitations, la connexion, des sessions avec rotation, et le mot de passe oublié.

## Prérequis et points à trancher au démarrage
- **Liste locale des mots de passe fuités** : choisir la source, sa taille et sa licence. Elle est embarquée dans le dépôt sans aucune donnée personnelle (uniquement des mots de passe, sans identifiants).
- **Seuils de limitation des tentatives** : nombre d'essais, fenêtre de temps, progression du blocage. Valeurs proposées par le coordinateur.

## Étapes
| # | Agent (modèle, effort) | Contenu | Règles |
|---|---|---|---|
| 1 | `dev-metier` (Opus, élevé) | **Domaine** : `Utilisateur` (e-mail, nom, rôle `CHEF` ou `OUVRIER`, actif), objets valeur `Email` et `MotDePasseEnClair` (politique de 12 caractères minimum, liste des mots de passe fuités), `Invitation` et `JetonReinitialisation` (usage unique, expiration), `Session` et `RefreshToken`, avec la famille de tokens pour détecter une réutilisation. Politique `peut_inviter`. **Ports** : `UtilisateurRepository`, `SessionRepository`, `InvitationRepository`, `JetonReinitialisationRepository`, `HacheurMotDePasse`, `EmetteurJeton`, `EnvoiEmail`, `LimiteurTentatives`. **Cas d'usage** : `SeConnecter`, `RafraichirSession`, `SeDeconnecter`, `InviterUtilisateur`, `AccepterInvitation`, `DemanderReinitialisation`, `ReinitialiserMotDePasse`, `ConsulterProfil`, `CreerPremierChef`. Connexions, échecs, invitations et changements de mot de passe sont écrits dans `JournalAudit`. | 00, 01, 02 |
| 2 | `dev-donnees` **(Opus, élevé)** | Repositories SQL et migrations. `Argon2HacheurMotDePasse`. `JwtEmetteurJeton` : algorithme fixé côté serveur, durée de 15 minutes. Tokens opaques **hachés** en base. `SmtpEnvoiEmail`, testé avec Mailpit. `SqlLimiteurTentatives`, par IP et par compte. Chargement de la liste des mots de passe fuités. CLI `creer-premier-chef` dans `app/cli/`, qui refuse de s'exécuter si un chef existe déjà. Branchement dans `app/composition/auth.py`. | 00, 03, 06, 07 |
| 3 | `dev-api` (Sonnet, moyen) | Routes `/api/auth/connexion`, `/rafraichir`, `/deconnexion`, `/invitations`, `/invitations/{jeton}/accepter`, `/reinitialisations` et `/reinitialisations/{jeton}`, plus `/api/moi`, qui reprend la route et le cas d'usage `ConsulterCapacites` du squelette (ADR 0008) : ils passent dans le module `auth`, et `ConsulterCapacites` reçoit une liste de fournisseurs de capacités. Cookies `HttpOnly`, `Secure` et `SameSite=Strict`. Dépendance `acteur_courant` dans `shared/api`. Réponse 429 en cas de blocage. Réponse identique à une demande de réinitialisation, que le compte existe ou non. | 00, 04 |
| 4 | `dev-frontend` (Sonnet, élevé) | Services : `useConnexion`, `useSession` (avec rafraîchissement automatique), `useInviter`, `useAccepterInvitation`, `useDemanderReinitialisation`, `useReinitialiser`. Pages : Connexion (selon la maquette), Accepter une invitation, Mot de passe oublié, Réinitialiser, Inviter un utilisateur (chef). Provider de session et garde de routes dans `src/app/`. | 00, 05 |
| 5 | `dev-frontend` (Sonnet, élevé) | **e2e Playwright** à 360 et 1280 px : création du premier chef en CLI → invitation d'un ouvrier (lien récupéré dans Mailpit) → l'ouvrier définit son mot de passe et se connecte → déconnexion. | 07 |

## Composants `ui` introduits
`Bouton` (principal, secondaire, danger), `Champ`, `ChampMotDePasse`, `Formulaire` (avec les erreurs par champ), `Carte`, `Pile`.

## Critères d'acceptation → tests
| Critère | Test qui le prouve | Couche |
|---|---|---|
| Le premier chef se crée en CLI ; la commande refuse s'il en existe déjà un ; il n'existe aucune inscription publique | `tests/unitaires/auth/test_creer_premier_chef.py`, `tests/integration/auth/test_cli_premier_chef.py`, test vérifiant qu'aucune route d'inscription n'existe dans OpenAPI | Service, données, API |
| Un chef invite un utilisateur ; le lien est à usage unique et à durée limitée ; un lien expiré ou déjà utilisé est refusé | `tests/unitaires/auth/test_inviter_utilisateur.py`, `test_accepter_invitation.py` (nominal, expiré, réutilisé), e2e | Domaine, service, e2e |
| Un ouvrier ne peut pas inviter (403) | Matrice `test_politiques_auth.py`, `tests/integration/auth/test_routes_invitations.py` | Domaine, API |
| Connexion, déconnexion, réinitialisation par e-mail | Tests unitaires des cas d'usage, tests d'intégration des routes, e2e | Toutes |
| La demande de réinitialisation donne la même réponse, que le compte existe ou non | `test_routes_reinitialisation.py` (comparaison du code et du corps de la réponse) | API |
| Un mot de passe de moins de 12 caractères, courant ou fuité est refusé avec un message clair | `tests/unitaires/auth/test_mot_de_passe.py` (hypothesis sur les longueurs), test Vitest de l'affichage de l'erreur | Domaine, frontend |
| Réutiliser un refresh token déjà utilisé révoque toute la session | `test_rafraichir_session.py`, `tests/integration/auth/test_rotation_refresh.py` | Service, API |
| La limitation des tentatives bloque après le seuil, par IP et par compte (§5.3) | `tests/contrats/test_limiteur_tentatives.py`, `tests/integration/auth/test_blocage_connexion.py` | Données, API |
| Un JWT expiré, falsifié ou signé avec un autre algorithme (`none`, HS/RS) est refusé | `tests/integration/auth/test_jwt_refuse.py` (paramétré) | Données, API |
| Les tokens d'invitation, de réinitialisation et de refresh sont stockés **hachés** | `tests/integration/auth/test_tokens_haches_en_base.py` (lecture directe de la base) | Données |
| Les connexions, les échecs et les invitations sont journalisés, sans donnée sensible | Tests des cas d'usage sur `MemoireJournalAudit` | Service |
| Les pages sont accessibles et responsives | axe dans Vitest, e2e à 360 et 1280 px | Frontend |

## Hors lot
Rôles supplémentaires, inscription publique, authentification à deux facteurs, modification du profil.
