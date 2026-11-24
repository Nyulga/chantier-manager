# Lot 06 – Notes, photos, documents

**Dépend de** : 04 · **Statut** : à faire · **Issue** : #6 · **Référence** : [ADR 0004](../decisions/0004-traitement-des-fichiers.md) · Peut se mener **en parallèle du lot 05**.

## Objectif
Centraliser les informations du terrain sur chaque chantier, avec une chaîne de contrôle des fichiers sans faille.

## Prérequis et points à trancher au démarrage
- **Suppression d'une note ou d'un fichier** : par son auteur seulement, par un chef du chantier, ou les deux ? Proposition : l'auteur et les chefs du chantier.
- Si le lot est mené en parallèle du lot 05 : chaque codeur travaille dans son propre worktree, et le coordinateur intègre les résultats (skill `lot`, §3).

## Étapes
| # | Agent (modèle, effort) | Contenu | Règles |
|---|---|---|---|
| 1 | `dev-metier` (Opus, élevé) | **Domaine** : `Note` (auteur, date, contenu non vide et de longueur limitée), `Document` (type photo ou PDF, nom d'origine nettoyé, taille, auteur, date, clé de stockage). Politiques `peut_ajouter`, `peut_consulter`, `peut_supprimer`. **Ports** : `NoteRepository`, `DocumentRepository`, `StockageFichiers`, `ScanneurAntivirus`, `AnalyseurFormat`, `AssainisseurImage`, et `ControleFichier`, le maillon commun de la **chaîne de responsabilité**. **Cas d'usage** : `AjouterNote`, `ListerNotes`, `EnvoyerFichier` (chaîne de contrôle, stockage, enregistrement, avec compensation en cas d'échec), `ListerDocuments`, `TelechargerDocument`, `SupprimerDocument`. Les suppressions sont écrites dans `JournalAudit`. | 00, 01, 02 |
| 2 | `dev-donnees` **(Opus, élevé)** | Maillons de la chaîne, dans cet ordre (fixé dans `app/composition/documents.py`) :<br>1. taille, comptée pendant la lecture du flux ;<br>2. `FiletypeAnalyseurFormat` (*magic bytes*) ;<br>3. `ClamdScanneurAntivirus`, avec un délai d'attente, et **refus si l'antivirus est indisponible** ;<br>4. `PillowAssainisseurImage`, qui réencode sans EXIF et convertit les HEIC en JPEG ;<br>5. `DisqueStockageFichiers`, avec un nom aléatoire, une écriture atomique et un stockage hors de la racine web.<br>Repositories SQL et migrations. Compensation : le fichier est supprimé si la transaction échoue. CLI `reconcilier-fichiers`, qui supprime les fichiers orphelins. | 00, 03, 06, 07 |
| 3 | `dev-api` (Sonnet, moyen) | Routes `/api/chantiers/{id}/notes`, `/api/chantiers/{id}/documents` (envoi en flux, `multipart`), `/api/documents/{id}` (téléchargement, avec `nosniff`, `CSP: sandbox`, `Content-Disposition: attachment` pour les PDF, et un nom de fichier jamais tiré directement d'une saisie). Codes 413 (trop lourd), 415 (format refusé), 422 (fichier rejeté par l'antivirus) et 503 (antivirus indisponible). | 00, 04 |
| 4 | `dev-frontend` (Sonnet, élevé) | Services : `useNotes`, `useAjouterNote`, `useDocuments`, `useEnvoyerFichier` (avec la progression). Composants et pages : fil de notes, bouton « Prendre une photo » toujours accessible sur mobile (`capture`), galerie de miniatures, liste des documents. Messages d'erreur clairs pour chaque refus (format, taille, antivirus). | 00, 05 |
| 5 | `dev-frontend` (Sonnet, élevé) | **e2e** à 360 et 1280 px : un ouvrier ajoute une note et une photo ; le chef les voit ; un utilisateur non rattaché ne peut pas les télécharger. | 07 |

## Composants `ui` introduits
`FilNotes`, `EnvoiFichier` (avec la progression), `Galerie`, `Miniature`, `ListeDocuments`, `BoutonPhoto` (le bouton principal mobile).

## Critères d'acceptation → tests
| Critère | Test qui le prouve | Couche |
|---|---|---|
| Tout utilisateur rattaché ajoute une note, affichée avec son auteur et sa date | Tests du cas d'usage, de la route et du composant, e2e | Toutes |
| Envoi d'une photo (JPEG, PNG, WebP, HEIC, 10 Mo maximum) ou d'un PDF (20 Mo maximum), puis consultation et téléchargement | `tests/integration/documents/test_envoi_fichiers.py` (un cas par format), e2e | API, e2e |
| Un fichier d'un autre format, trop lourd ou à l'extension falsifiée est refusé | Tests paramétrés : PNG renommé en `.pdf`, exécutable renommé en `.jpg`, fichier de 10 Mo plus 1 octet coupé **pendant la lecture** | Données, API |
| Le fichier de test EICAR est refusé ; un antivirus indisponible entraîne le refus de tout envoi | `tests/contrats/test_scanneur_antivirus.py` (ClamAV réel), `test_antivirus_indisponible.py` | Données, API |
| Les photos stockées ne contiennent plus aucune métadonnée EXIF (dont le GPS) ; un HEIC est converti en JPEG | `tests/contrats/test_assainisseur_image.py` (fichiers de test avec GPS) | Données |
| Un fichier n'est accessible qu'aux utilisateurs autorisés, jamais par une URL publique | `test_telechargement_cloisonne.py` (404 hors périmètre), test vérifiant que le dossier de stockage n'est pas servi | API |
| Un échec de transaction ne laisse pas de fichier orphelin, et `reconcilier-fichiers` nettoie les restes | `test_envoyer_fichier.py` (compensation), `test_reconcilier_fichiers.py` | Service, données |
| Les en-têtes de téléchargement sont corrects (`nosniff`, `sandbox`, `attachment` pour les PDF) | `test_entetes_telechargement.py` | API |
| L'ordre de la chaîne est garanti | `tests/application/documents/test_chaine_controle.py` (espions sur les fakes) | Service |

## Hors lot
Stockage S3, édition de documents, formats autres que PDF et photos, modification d'une note.
