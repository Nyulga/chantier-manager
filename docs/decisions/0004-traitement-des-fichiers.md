# ADR 0004 : envoi, contrôle et stockage des fichiers

- **Statut** : accepté
- **Date** : 2026-11-22

## Contexte

Les utilisateurs envoient des photos et des PDF depuis des téléphones. Ces fichiers sont un vecteur d'attaque classique : fichiers malveillants, formats falsifiés, PDF piégés, saturation du disque. Les photos posent aussi un problème RGPD : leurs données EXIF contiennent souvent la position GPS.

## Décision

**Chaîne de contrôle**, appliquée dans le service, dans cet ordre. Si une étape échoue, le fichier est refusé et rien n'est conservé.

1. **Taille** : `client_max_body_size` dans Nginx, plus un comptage dans l'API pendant la lecture du flux. Limites : 10 Mo par photo, 20 Mo par PDF.
2. **Format réel** : détecté par les *magic bytes* (bibliothèque `filetype`). Liste blanche : PDF, JPEG, PNG, WebP, HEIC. L'extension et le `Content-Type` du client sont ignorés.
3. **Antivirus** : ClamAV (`clamd`), via le port `ScanneurAntivirus`. Si l'antivirus est indisponible ou dépasse son délai, l'envoi est **refusé** (*fail closed*).
4. **Assainissement des photos** : réencodage avec Pillow et pillow-heif, qui supprime toutes les métadonnées (EXIF, GPS) et neutralise les contenus parasites. Les HEIC sont convertis en JPEG pour être affichables partout.
5. **Stockage** : nom aléatoire (UUID v7), dans un dossier hors de la racine web, via le port `StockageFichiers` (implémentation `LocalFileStorage` en V1). Le nom d'origine est conservé uniquement en base, nettoyé, pour l'affichage.

**Restitution**
- Uniquement par une route de l'API, après vérification des droits sur le chantier.
- En-têtes : `X-Content-Type-Options: nosniff`, `Content-Security-Policy: sandbox`, et `Content-Disposition: attachment` pour les PDF, qui ne sont jamais affichés dans la page.
- Nginx peut servir le fichier via `X-Accel-Redirect`, après l'autorisation donnée par l'API.

## Alternatives écartées

| Option | Raison du rejet |
|---|---|
| **Fichiers servis directement par Nginx depuis un dossier public** | Aucun contrôle d'accès. |
| **Confiance dans l'extension ou le `Content-Type`** | Trivialement falsifiables. |
| **Pas d'antivirus** | Contraire à l'exigence de sécurité, surtout pour les PDF partagés entre utilisateurs. |
| **Stockage objet (S3) dès la V1** | Inutile pour l'instant. Le port `StockageFichiers` permettra de l'ajouter sans toucher au métier. |

## Conséquences

- Le conteneur ClamAV consomme environ 1 Go de RAM et met à jour ses signatures (freshclam).
- Le réencodage consomme du CPU : il reste synchrone en V1, vu les volumes attendus.
- Le stockage et la base peuvent diverger en cas de panne. On applique une compensation au moment de l'envoi, et une commande CLI de réconciliation supprime les fichiers orphelins.
