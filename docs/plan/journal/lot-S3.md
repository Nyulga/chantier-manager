# Journal du lot S3 – Mise en ligne

**Issue** : #12 · **Statut** : terminé le 2026-11-22 · **Adresse** : https://chantier-ultra.ddns.net

## Ce qui a été déployé

- **Source** : la branche `main` (fusion des PR #25 et #26), clonée sur le serveur Ubuntu 24.04.
- **Conteneurs** : `chantier-api` (FastAPI, un seul worker, base SQLite dans le volume `chantier-donnees`) et `chantier-web` (fichiers statiques servis par Caddy). Les deux tournent en non-root (uid 10001), sans port publié sur l'hôte.
- **Proxy** : le Caddy déjà présent pour vtt sur son réseau Docker. Un bloc `chantier-ultra.ddns.net` a été ajouté à la fin de le Caddyfile de cet autre projet, avec une sauvegarde préalable, `caddy validate`, puis un rechargement à chaud, sans coupure pour l'autre projet.
- **Migrations** : appliquées automatiquement au premier démarrage de l'API.

## Décision du propriétaire au moment de la mise en ligne

Le mot de passe d'accès au site (`basic_auth`) a d'abord été posé, puis **retiré à la demande du propriétaire** : le site est une **démonstration publique**.
- **Conséquence acceptée** : n'importe qui peut agir en chef. On n'y saisit donc aucune donnée réelle.
- Le mot de passe généré et son empreinte ont été supprimés du poste. Ils ne sont jamais entrés dans le dépôt.
- `deploy/Caddyfile.extrait`, `deploy/README.md` et `docs/plan/squelette.md` décrivent désormais cette version publique, et expliquent comment remettre une protection.

## Vérifications en production (depuis l'extérieur, en HTTPS)

| Contrôle | Résultat |
|---|---|
| `GET /` | 200, certificat Let's Encrypt valide |
| `GET /api/health` | 200 |
| `GET /api/chantiers` (profil chef) | 200, liste vide |
| `GET /api/docs` | 404 : documentation masquée |
| `POST` de 100 Ko sur l'API | 413 : limite de 64 Ko |
| En-têtes | CSP stricte, HSTS, `X-Frame-Options: DENY` |
| L'autre projet servi par le même Caddy | `/health` et `/docs` répondent 200 ; son bloc Caddy est inchangé |

**Test complet préalable**, sur Docker Desktop, avec les mêmes images : créer un chantier (le budget `1E3` revient en `1000.00`), ajouter une étape, la démarrer, la signaler, la valider (100 %). Le budget est bien masqué en profil ouvrier.

## Retour arrière

- **Caddy** : deux sauvegardes horodatées du Caddyfile ont été faites à côté de lui, avant chaque modification. Pour revenir en arrière, `cat` de la sauvegarde vers `Caddyfile`, puis `caddy reload`.
- **Application** : `docker compose -f compose.prod.yaml down` dans le dossier `deploy/` du clone sur le serveur. Le volume `chantier-donnees` est conservé.

## Reporté à la phase 2

- Les points de sécurité suivis dans #13 à #16 : réseau Docker dédié, durcissement des conteneurs, épinglage des images, journaux.
- Le pare-feu, fail2ban et la sauvegarde automatique chiffrée.
- Le passage à PostgreSQL.
