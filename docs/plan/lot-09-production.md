# Lot 09 – Production

**Dépend de** : 08 · **Statut** : à faire · **Issue** : #9

## Objectif
Mettre l'application en ligne sur le serveur Ubuntu personnel, de façon sûre, sauvegardée et restaurable.

## Prérequis à préparer par l'utilisateur
- **Un nom de domaine**, pour le TLS et pour les e-mails.
- **Un DNS dynamique**, si l'adresse IP de la box change.
- **Un accès à la box**, pour rediriger uniquement les ports 80 et 443.
- **Un compte SMTP** chez un fournisseur établi dans l'UE.
- **Un stockage dans l'UE** pour la copie des sauvegardes hors du domicile.
- **Un accès SSH par clé** au serveur.

**Aucune commande n'est exécutée sur le serveur réel sans l'accord explicite de l'utilisateur**, donné pour chaque commande ou pour une procédure entière.

## Étapes
| # | Agent (modèle, effort) | Contenu | Règles |
|---|---|---|---|
| 1 | `dev-socle` **(Opus, élevé)** | **Images de production** : multi-étapes, utilisateur non root, système de fichiers en lecture seule quand c'est possible, scan Trivy. **`docker-compose.prod.yml`** : `api`, `web` (Nginx qui sert la SPA et fait proxy vers `/api`), `db` et `clamav` ; volumes pour les données et les fichiers ; *healthchecks* ; redémarrage automatique. Migrations Alembic appliquées au démarrage, après une sauvegarde. | 00 |
| 2 | `dev-socle` **(Opus, élevé)** | **Nginx** : TLS Let's Encrypt avec renouvellement automatique, redirection du HTTP vers le HTTPS, en-têtes de sécurité, `client_max_body_size`, `X-Accel-Redirect` pour les fichiers. **SMTP** : configuration de SPF, DKIM et DMARC sur le domaine. | 00 |
| 3 | `dev-socle` **(Opus, élevé)** | **Procédure de durcissement du serveur**, préparée sous forme de scripts relus : SSH par clé uniquement, fail2ban, ufw (80, 443 et SSH), `unattended-upgrades`. **L'utilisateur exécute ou autorise chaque commande.** | 00 |
| 4 | `dev-socle` **(Opus, élevé)** | **Sauvegardes** restic, chiffrées et quotidiennes : base (`pg_dump`) et fichiers, rétention définie, copie hors du domicile dans l'UE. **Timers systemd** pour `purger`, `reconcilier-fichiers` et les sauvegardes. | 00 |
| 5 | `dev-socle` **(Opus, élevé)** avec l'utilisateur | **Test de restauration complet sur une machine vierge**, documenté pas à pas. | — |
| 6 | `securite` (Opus, élevé) | Contrôle final avant la mise en ligne, avec le verdict « prêt pour la production ». | — |
| 7 | Coordinateur | **README d'exploitation** : installation, configuration, mise à jour, sauvegarde, restauration, rotation des secrets. | — |

## Composants `ui` introduits
Aucun.

## Critères d'acceptation → tests
| Critère | Preuve | Couche |
|---|---|---|
| L'application démarre sur le serveur avec une seule commande `docker compose up -d` (§5.5) | Procédure exécutée, trace dans le journal du lot | Production |
| HTTPS, et le HTTP redirige vers le HTTPS (§5.5) | Test `curl` scripté depuis l'extérieur | Production |
| Les migrations s'appliquent automatiquement, sans perte de données (§5.5) | Test du cycle upgrade et downgrade (règle 07), et sauvegarde vérifiée avant migration | Données, production |
| Sauvegardes automatiques et chiffrées, avec une copie hors du domicile, et **restauration testée** avec succès (§5.5) | Compte rendu du test de restauration dans `docs/exploitation/` | Production |
| README d'installation, de configuration et de restauration (§5.5) | Relecture par l'utilisateur | Documentation |
| Scan ZAP de l'instance de production propre | Rapport ZAP archivé | Production |
| Conteneurs sans droits root, et images sans vulnérabilité moyenne ou plus | `docker inspect`, rapport Trivy | Production |

## Hors lot
Haute disponibilité, supervision avancée (à envisager après la V1).
