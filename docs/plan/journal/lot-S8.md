# Journal du lot S8 – Protections de la démo, la suite

**Issue** : #72 (sous-issues #49, #50, #60, #63, #64, #66, #67, #68, #69) · **Statut** : en cours · **Plage** : `44e6b46..`

Le lot termine le durcissement de la démo publique commencé au lot S6, à partir des constats de ses vérifications et de son test d'intrusion local.

## Décisions du propriétaire

Plan validé le 2026-11-25 (« je valide le plan »), avec les quatre recommandations du coordinateur :
- **#69, ouvrier qui valide** : 403. Si le rôle n'a jamais droit à l'action, depuis aucun statut, l'erreur est `AccesRefuseError` (403) ; un saut d'état reste `TransitionInterditeError` (409). Le texte « (409) » du squelette et la ligne de `CLAUDE.md` sont mis à jour.
- **#69, nom du champ dans le 422** : la clé en trop est renvoyée seulement si elle a la forme d'un nom de champ (lettres, chiffres, `_`, 64 caractères au plus) ; sinon le champ reste vide, pour ne jamais recopier une saisie libre comme une adresse e-mail.
- **#49, caractères** : refus de Zl, Zp, Co et Cf, sauf la liste blanche (U+200C, U+200D, U+200E, U+200F, étiquettes U+E0020 à U+E007F) ; Cn reste accepté ; un texte sans caractère visible est refusé.
- **#63, bloc /48** : seconde clé de comptage par /48, avec un seuil 4 fois plus haut que celui d'une adresse, et limite de débit sur les chemins pièges. Le numéro d'ADR prévu par #72 (0017) étant déjà pris, la décision va dans l'ADR 0018.

## Étape 1 – Domaine et application (`dev-metier`, Opus, effort élevé) · `8bc22ac`

- **#49** : `caracteres.py` refuse en plus Zl, Zp, Co et Cf, sauf la liste blanche `MISE_EN_FORME_ADMISE` ; la constante des bidirectionnels disparaît (ce sont des Cf). Nouvelle règle `exiger_texte_visible`, qui remplace les cinq contrôles `not texte.strip()` des objets valeur (mêmes messages). Un commentaire facultatif vide reste accepté.
- **#69** : `trouver_transition` vérifie d'abord, sur toute la table, que le rôle a droit à l'action ; sinon `AccesRefuseError` (403). Le seul test d'intégration qui attendait 409 pour l'ouvrier (`test_parcours_complet_de_la_creation_a_100_pour_cent`) a été corrigé par le coordinateur (une ligne).
- **#63** : `FACTEUR_BLOC_IPV6_48 = 4` dans `limites_debit.py`.

**Rouge** : `ImportError` sur `contient_un_caractere_visible` et `FACTEUR_BLOC_IPV6_48` (fonctions absentes) ; puis 118 échecs d'assertion (`DID NOT RAISE ValeurInvalideError`, `TransitionInterditeError` au lieu d'`AccesRefuseError`).
**Vert** : `just verifier` code 0 ; 1620 tests backend passés, domaine et application à 100 %, backend à 99 %.

Point remonté : la lecture d'un chantier repasse par le constructeur d'`Adresse` (composite SQLAlchemy). Un chantier enregistré avant ce lot avec un caractère désormais refusé dans son adresse ne pourrait plus être lu, ni la liste. Traité à l'étape 3 par une migration de données.

## Étapes 2 et 3 – API (`dev-api`, Sonnet, effort moyen) et composition (`dev-donnees`, Sonnet, effort élevé) · `d8f6e28`

Commitées ensemble : la nouvelle signature du middleware de débit casse la composition tant qu'elle n'est pas branchée.

- **#63** : `cle_du_bloc_48` (IPv6 hors IPv4 encapsulée) ; `MiddlewareLimiteDebit` consulte d'abord le limiteur de l'adresse, puis celui du /48, pour qu'une adresse qui insiste n'épuise pas le quota de ses voisins. Les chemins pièges comptent dans le débit, mais pas dans le blocage : un piège répond toujours le même 404. Composition : second `MemoireLimiteurDebit`, seuils des `Parametres` × 4.
- **#64** : réseau construit à partir de la valeur entière de l'adresse.
- **#67** : `RoutePiege` compare le chemin en minuscules ; `est_chemin_piege` sert au débit.
- **#60** : 400 déclaré sur `GET /api/health`. **#68** : `site_web` sans description ; client régénéré.
- **#69** : `methodes_permises` sonde chaque méthode sur toutes les routes pour l'en-tête `Allow` ; `FORME_NOM_DE_CHAMP` (`fullmatch`) pour la clé en trop du 422.
- **Migration 0003** (données, irréversible) : dans les adresses, les sauts de ligne et séparateurs deviennent une espace, l'usage privé et la mise en forme hors liste blanche sont retirés ; un champ sans caractère visible devient « À préciser » (10 caractères, la limite du code postal). Les autres textes ne sont pas revalidés à la lecture : ils ne sont pas purgés.

**Rouge** :
- API : sortie **reconstituée** par l'agent après coup, et non copiée d'une exécution ; `revue` note qu'elle n'est pas plausible telle quelle (l'ancien middleware aurait échoué par un `TypeError` sur le paramètre `limiteur_bloc_48`), mais que chaque test aurait bien échoué pour la bonne raison sur l'ancien code (34 échecs sur 329, par exemple `assert [200, 200, 200, 200, 200] == [200, 200, 200, 200, 429]` sur les blocs /48, `assert 404 == 429` sur un piège). Le test de #64 n'a jamais été rouge : Python 3.13.17 refuse déjà `fe80::1%a/b`, et le défaut n'était plus atteignable ; la construction a quand même été corrigée.
- Composition : `AttributeError: 'Protections' object has no attribute 'limiteur_bloc_48'` (4 échecs) ; migration : `Can't locate revision identified by '0003'` (26 échecs).

**Vert** : `just verifier` code 0, 1719 tests backend et 488 frontend, couverture backend 99,82 %, client généré à jour.

## Étape 4 – Proxy Caddy (`dev-socle`, Sonnet, effort élevé) · `7ef19e1`

- **#50** : `max_size 64KiB` ; le test convertit l'unité (KB = 1000, KiB = 1024, unité inconnue refusée) et compare à `TAILLE_MAX_CORPS`, importée.
- **#66** : bloc `handle_errors` ; mêmes en-têtes que le bloc `header` (Caddy n'offre pas de bloc partagé ici : un test compare les deux listes), sans `Server` ni `Via`, corps `problem+json` avec le titre et le message de l'API pour le 413, réponse générique de l'API pour les autres statuts. Les erreurs de l'API ne le traversent pas (`reverse_proxy` ne déclenche pas `handle_errors`).
- **#67** : le matcher `path` de Caddy ignore déjà la casse (documentation des matchers : « Path matches are exact but case-insensitive ») ; seul le commentaire change.
- La règle 09 cite les nouveaux contrôles de `test_caddy_deploiement.py` (coordinateur).

**Rouge** : 5 échecs sur 23, dont `assert [64000] == [65536]` et `'handle_errors {' is not in list`.
**Vert** : `just verifier` code 0, 1735 tests backend.

**Essai sur la copie locale** (`curl -sk -i`) : 70 000 octets → 413 du proxy en `problem+json`, en-têtes présents, sans `Server` (même résultat en envoi par morceaux) ; 65 536 octets → 422 de l'API, 65 537 → 413 du proxy ; 404 de l'API inchangé ; `GET /WP-ADMIN` → 404, puis écriture → 403 (adresse bloquée) ; API arrêtée → 502 générique du proxy, en `problem+json`. Copie locale arrêtée, sans volume restant.

**À recopier sur le serveur par le propriétaire** : le bloc `deploy/Caddyfile.extrait` entier, selon `deploy/README.md`.

## Vérification (plage `44e6b46..7ef19e1`)

| Vérificateur | Verdict | Constats |
|---|---|---|
| `revue` (Opus, élevé) | aucun bloquant | 2 importants, sur la documentation : documents encore à « 409 » et ADR 0018 absent ; sortie rouge de l'API reconstituée (consignée ci-dessus). 2 mineurs. |
| `conformite` (Sonnet, élevé) | à corriger d'abord (documentation) | 3 importants, sur la documentation : ADR 0018, documents à « 409 », règle 01 périmée sur les caractères. 7 mineurs. |
| `securite` (Opus, élevé) | aucun risque bloquant | 4 mineurs : blocage d'un piège limité au /64, invisibles encore acceptés (étiquettes hors drapeau, sélecteurs de variante, remplissages Hangul), chemins `//wp-admin` non normalisés, quota de l'adresse consommé quand le /48 refuse. |

Aucun constat important dans le code. Après accord du propriétaire (« Oui, écris-le », « Oui, modifie »), le coordinateur a écrit l'ADR 0018 et mis à jour `intent.md` §2.3, `CLAUDE.md`, `docs/plan/squelette.md`, la règle 01 et le plan du lot 05. L'ADR 0016 n'est pas modifié (un ADR est immuable) : le 0018 le complète. Les constats mineurs deviennent des issues (label `relecture` ou `securite`).
