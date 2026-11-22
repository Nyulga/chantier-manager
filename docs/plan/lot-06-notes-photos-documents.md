# Lot 06 – Notes, photos, documents

**Dépend de** : 04 · **Statut** : à faire · **Référence** : [ADR 0004](../adr/0004-traitement-des-fichiers.md)

## Objectif
Centraliser les informations du terrain sur chaque chantier, avec une chaîne de contrôle des fichiers sans faille.

## Contenu
- **Notes** : entité `Note` (auteur, date, contenu) ; ajout et affichage en fil sur le chantier. Le contenu est stocké tel quel, puis échappé à l'affichage.
- **Documents** : entité `Document` (type photo ou PDF, nom d'origine nettoyé, taille, auteur, date, clé de stockage).
- **Chaîne de contrôle** : limite de taille → *magic bytes* → ClamAV (refus si indisponible) → réencodage des photos sans EXIF (avec conversion des HEIC en JPEG) → nom aléatoire → stockage.
- **Ports** : `StockageFichiers` (`LocalFileStorage`, plus une implémentation mémoire), `ScanneurAntivirus` (`ClamdScanneur`, plus une implémentation de test), `AnalyseurFormat`, `AssainisseurImage`.
- **Compensation** : si le commit échoue, le fichier stocké est supprimé. Une CLI `reconcilier-fichiers` supprime les fichiers orphelins.
- **Téléchargement** : route protégée par les droits, en-têtes `nosniff`, `CSP: sandbox`, et `attachment` pour les PDF.
- **Frontend** : fil de notes, envoi de fichiers (prise de photo directe sur mobile avec `capture`), galerie de miniatures, liste des documents, messages d'erreur clairs (format, taille, fichier refusé).
- **Tests** : fichier EICAR refusé, PNG renommé en `.pdf` refusé, EXIF GPS absent après envoi, fichier trop volumineux coupé dès la lecture du flux, accès interdit à un utilisateur non rattaché.

## Critères d'acceptation
- [ ] Tous les critères « Notes, photos et documents » d'`intent.md` §5.1.
- [ ] Aucun fichier n'est accessible sans passer par l'API (test).

## Hors lot
Stockage S3, édition de documents, formats autres que PDF et photos.
