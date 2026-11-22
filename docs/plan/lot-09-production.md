# Lot 09 – Production

**Dépend de** : 08 · **Statut** : à faire

## Objectif
Mettre l'application en ligne sur le serveur Ubuntu personnel, de façon sûre, sauvegardée et restaurable.

## Contenu
- **Images Docker de production** : multi-étapes, utilisateur non root, système de fichiers en lecture seule quand c'est possible, et scan Trivy sans vulnérabilité moyenne ou plus.
- **`docker-compose.prod.yml`** : `api`, `web` (Nginx qui sert la SPA et fait proxy vers `/api`), `db`, `clamav` ; volumes pour les données et les fichiers ; *healthchecks* ; redémarrage automatique.
- **Nginx** : TLS Let's Encrypt avec renouvellement automatique, redirection du HTTP vers le HTTPS, en-têtes de sécurité, `client_max_body_size`, `X-Accel-Redirect` pour les fichiers.
- **Migrations** Alembic appliquées automatiquement au démarrage, avec une sauvegarde préalable.
- **Durcissement du serveur** :
  - SSH par clé uniquement (ou via un VPN), fail2ban ;
  - pare-feu ufw (80, 443 et SSH) ;
  - `unattended-upgrades` ;
  - seuls les ports 80 et 443 sont redirigés sur la box.
- **SMTP de production**, chez un fournisseur établi dans l'UE, avec SPF, DKIM et DMARC configurés sur le domaine.
- **Sauvegardes** :
  - quotidiennes, chiffrées (par exemple avec restic) ;
  - base (`pg_dump`) et fichiers ;
  - rétention définie ;
  - **copie hors du domicile dans l'UE**.
- **Test de restauration** complet sur une machine vierge, documenté.
- **Tâches planifiées** : timers systemd pour `purger`, `reconcilier-fichiers` et les sauvegardes.
- **README d'exploitation** : installation, configuration, mise à jour, sauvegarde, restauration, rotation des secrets.

## Critères d'acceptation
- [ ] Tous les critères « Déploiement » d'`intent.md` §5.5.
- [ ] Un scan ZAP de l'instance de production est propre.

## Hors lot
Haute disponibilité, supervision avancée (à envisager après la V1).
