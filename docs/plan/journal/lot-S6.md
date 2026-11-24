# Journal du lot S6 – Sécuriser la démo

**Issue** : #45 · **Statut** : en cours depuis le 2026-11-24 · **Plage** : `ee4b35a..`

Le lot fait suite au premier test d'intrusion local (règle 08) et à la demande du propriétaire de protéger la démo publique, où l'écriture est ouverte à tous. Le plan a été validé par le propriétaire le 2026-11-24.

## Décisions du propriétaire

- **Limites de débit** : 20 écritures et 120 lectures par minute et par adresse ; une adresse qui touche un piège est bloquée en écriture pendant 1 heure.
- **Plafonds de volume** : 100 chantiers en tout, 30 étapes par chantier. La démo n'est **pas** remise à zéro : une fois le plafond atteint, plus aucune création n'est possible, et le propriétaire décidera de la suite.
- **Mise en ligne** : étape séparée, après le lot, avec accord pour chaque commande sur le serveur (le bloc Caddy du serveur change).
- **Hors lot** : fail2ban sur le serveur (lot 08) ; le code d'erreur d'un ouvrier qui tente de valider (issue à part).

## Étape 1 – Domaine et services (`dev-metier`, Opus, effort élevé)

**Textes propres (constat M4)** : nouvelle garde `app/shared/domain/caracteres.py`, appliquée à chaque champ texte. Sont refusés les caractères de contrôle (`Cc`), les demi-codets isolés (`Cs`) et les caractères bidirectionnels (U+202A–U+202E, U+2066–U+2069, risque d'usurpation d'affichage). Champs sur une ligne (nom, client, voie, code postal, ville, titre d'étape) : aucun contrôle admis. Commentaire d'une transition : `\n`, `\r` et `\t` admis. Le message d'erreur est fixe et désigne le champ (ADR 0008).

**Plafonds** : `LIMITE_CHANTIERS = 100`, `LIMITE_ETAPES_PAR_CHANTIER = 30`, nouvelle `PlafondAtteintError` (`shared/application/erreurs.py`). Le droit est vérifié d'abord, puis le plafond, dans la transaction et avant toute écriture.

**Découpage des couches** : une première version ajoutait un comptage au port et à l'infrastructure ; le propriétaire l'a refusé (pas d'entorse au découpage). Le comptage s'appuie sur les lectures existantes (`lister()`, et la lecture des étapes déjà faite pour l'ordre), bornées par ces mêmes plafonds. Infrastructure et tests de contrat intacts (`git diff --stat` vide). Le besoin d'un garde-fou automatique est suivi dans l'issue #46.

**Donnée de test corrigée** : `tests/integration/etapes/test_api_tableau_de_bord.py` créait 51 étapes sur un seul chantier ; elle les répartit désormais sur plusieurs chantiers.

**Rouge** : textes `115 failed, 10 passed` (`Failed: DID NOT RAISE ValeurInvalideError`) ; plafonds `4 failed, 10 passed` (`DID NOT RAISE PlafondAtteintError`).
**Vert** (`just verifier`, coordinateur) : `797 passed`, couverture backend 100 %, domain et application `687 0 48 0 100%`, 8 contrats tenus, `458` tests frontend.

**Reste pour l'étape 3 (`dev-api`)** : `PlafondAtteintError` → 409, tests d'intégration du 409 et du 422 sur un caractère nul.

## Étape 2a – Ports de la limite de débit et des pièges (`dev-metier`, Opus, effort élevé)

**Ajustement du plan** : pour qu'aucun agent ne sorte de sa couche, l'ancienne étape 2 est découpée. `dev-metier` écrit les ports (2a), `dev-donnees` leurs implémentations en mémoire (2b), `dev-api` les middlewares (3), puis `dev-donnees` les branche dans la composition (3b).

**Livré** (`shared/application` seulement) : `CategorieAcces` (lecture, écriture), ports `LimiteurDebit.consommer(adresse, categorie) -> int | None` (délai en secondes entières, au moins 1) et `ListeAdressesBloquees` (`bloquer`, `est_bloquee`). Constantes des décisions du propriétaire dans `limites_debit.py` : fenêtre de 1 min, 20 écritures, 120 lectures, blocage de 1 h. Hypothèse écrite : stockage en mémoire, un seul processus API (ADR 0015).

**TDD** : pas de phase rouge, car il n'y a pas de comportement (des `Protocol` et des constantes). Le test `test_limites_debit.py` fige les valeurs décidées.
**Vert** (`just verifier`, coordinateur) : `799 passed`, couverture 100 %, 8 contrats tenus, `458` tests frontend.

**Décision du coordinateur** : une adresse bloquée par un piège reçoit un 403 sur ses écritures, sans délai annoncé ; `est_bloquee` suffit.

## Étape 2b – Limiteur et liste d'adresses bloquées en mémoire (`dev-donnees`, Sonnet, effort élevé)

**Livré** (`shared/infrastructure`, `composition/parametres.py` et leurs tests seulement) :
- `MemoireLimiteurDebit(horloge, seuils, fenetre, cles_max)` : fenêtre glissante, une file d'horodatages par adresse et catégorie, verrou, au plus 5 000 clés suivies (au-delà, la plus ancienne est évincée plutôt que de refuser les nouvelles adresses, ce qui serait un déni de service) ;
- `MemoireListeAdressesBloquees(horloge, duree, adresses_max)` : au plus 10 000 adresses, éviction du blocage le plus proche de son terme ;
- `HorlogeAvancable`, pour tester le temps sans attendre ;
- `Parametres` : `documentation_exposee = False`, `hotes_acceptes = ["localhost", "127.0.0.1"]`, `taille_max_corps = 64 Ko`.

Les suites de contrat sont prêtes à recevoir une seconde implémentation (base ou Redis) ; il n'y en a qu'une pendant le squelette (un seul processus API, ADR 0015).

**Rouge** : `16 failed, 6 passed` avec une première version qui permettait tout (`assert None == 60`, `assert 400 == 50`, `est_bloquee` toujours faux) ; `AttributeError` sur les nouveaux paramètres.
**Vert** (`just verifier`, coordinateur) : `840 passed`, couverture 100 %, 8 contrats tenus, `458` tests frontend.

**Limite connue** : le test de concurrence passe aussi sans verrou (section critique trop courte face au GIL) ; le verrou est justifié par lecture.

**Pour la suite** : `compose.prod.yaml` devra définir `CHANTIER_HOTES_ACCEPTES` (étape `dev-socle`) ; les tests de l'API construiront leurs `Parametres` avec l'hôte `testserver` et la documentation exposée.

## Étape 3 – Protections HTTP (`dev-api`, Sonnet, effort moyen)

**Livré** (`*/api/` et tests seulement), dans `shared/api/` : `MiddlewareEnTetesSecurite` (valeurs identiques au Caddyfile, vérifié par test), `MiddlewareTailleCorps` (413, y compris sans `Content-Length`), `MiddlewareLimiteDebit` (429 + `Retry-After`, `/api/health` exclu), `MiddlewareBlocageEcritures` (403 neutre sur les écritures d'une adresse bloquée), `creer_routeur_pieges` (fausses adresses : 404 identique à une adresse inconnue, et blocage), champ piège `site_web` (403 neutre avant la validation et le cas d'usage). `PlafondAtteintError` → 409, documenté dans OpenAPI. Budget accepté en texte décimal uniquement. `HEAD /api/health`.

**Écarté** : nommer le champ en trop dans le 422. L'ADR 0008 interdit de renvoyer une clé inventée par le client (elle peut contenir une donnée personnelle) ; la demande du plan était une erreur du coordinateur.

**Temporaire** : les routeurs acceptent encore une liste d'adresses bloquées absente, le temps que l'étape 3b la branche ; ce cas sera retiré ensuite.

**Rouge** : `3 failed, 2 passed` sur les plafonds et le budget (`PlafondAtteintError` non traduite, `assert 201 == 422`) ; les autres tests échouaient à l'import des middlewares absents.
**Vert** (`just verifier`, coordinateur) : `911 passed`, couverture 100 %, 8 contrats tenus, `458` tests frontend.

## Étape 3c – Hôtes acceptés (`dev-api`, Sonnet, effort moyen)

`MiddlewareHotesAcceptes(app, hotes)` dans `shared/api/hotes_acceptes.py` : un `Host` absent ou hors liste reçoit un 400 au format RFC 9457 (« Hôte non reconnu. », sans recopier l'hôte). Il remplace `TrustedHostMiddleware` de Starlette, qui répond en texte brut (contraire à l'ADR 0008). Comparaison sans le port et sans la casse ; le démarrage (`lifespan`) passe.

**Ordre d'empilement retenu**, de l'extérieur vers l'intérieur : en-têtes de sécurité, hôtes, taille, blocage, débit.

**Rouge** : `ModuleNotFoundError: app.shared.api.hotes_acceptes`. **Vert** (`just verifier`, coordinateur) : `922 passed`, couverture 100 %.

## Étape 3b – Branchement dans la composition (`dev-donnees`, Sonnet, effort élevé)

**Livré** : `composition/protections.py` crée une seule fois par application le limiteur et la liste d'adresses bloquées, et empile les middlewares (de l'extérieur vers l'intérieur : en-têtes, hôtes, taille, blocage, débit). `main.py` : documentation et `openapi.json` seulement si `documentation_exposee`, pas de redirection de la barre oblique finale, routeur des pièges à la racine, liste passée aux routeurs. `Parametres` gagne `ecritures_par_minute` et `lectures_par_minute`, par défaut égaux aux décisions du propriétaire (20 et 120) ; seuls les tests les relèvent.

**Tests** : la fixture `client` relève les seuils et expose la documentation ; la nouvelle fixture `client_protege` garde les réglages de production. `test_protections_application.py` et `test_protections_enveloppe.py` prouvent chaque protection sur l'application réelle. `test_champ_piege_routes.py` est supprimé : il montait les routeurs à la main, ses cas sont repris sur l'application réelle.

**Rouge** : `12 failed, 5 passed` (`openapi.json` en 200, `/api/chantiers/` en 307, 201 au lieu de 429 ou 403, ni 413 ni 400). **Vert** (`just verifier`, coordinateur) : `943 passed`, couverture 100 %. `just client` produit toujours le schéma complet.

**À suivre** : `just e2e` demande `CHANTIER_ECRITURES_PAR_MINUTE` et `CHANTIER_LECTURES_PAR_MINUTE` relevés dans la configuration Playwright (étape 4) ; `deploy/` doit définir `CHANTIER_HOTES_ACCEPTES` (étape 5) ; le paramètre temporaire des routeurs devient obligatoire (`dev-api`).
