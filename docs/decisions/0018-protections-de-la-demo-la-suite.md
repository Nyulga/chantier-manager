# ADR 0018 – Protections de la démo, la suite : bloc /48, pièges, caractères et refus de droit

- **Statut** : accepté (squelette). Il complète l'ADR 0016 et l'ADR 0008 (contrat d'erreur).
- **Date** : 2026-11-25 (lot S8).

## Contexte
Les vérifications et le test d'intrusion local du lot S6 ont laissé plusieurs écarts (issues #49, #63, #67, #69) :
- l'ADR 0016 compte une adresse IPv6 par son bloc /64, « pour qu'un robot ne puisse pas changer d'adresse à chaque requête ». C'est vrai seulement à l'intérieur d'un /64. Or beaucoup d'abonnés reçoivent un /56 ou un /48, tunnels gratuits compris : avec un /48, un robot dispose de 65 536 blocs /64, donc d'autant de quotas. Les chemins pièges, eux, n'étaient soumis à aucune limite de débit ;
- un piège écrit en majuscules (`/WP-ADMIN`) atteignait l'API sans bloquer l'adresse ;
- les textes acceptaient encore des caractères invisibles : séparateurs de ligne et de paragraphe, usage privé, caractères de mise en forme, et un texte sans aucun caractère visible ;
- un ouvrier qui tentait de valider une étape recevait un 409 (« pas dans le bon état »), alors qu'il n'en aura jamais le droit.

## Décision
- **Seconde limite de débit par bloc /48**, pour les adresses IPv6 (hors IPv4 encapsulée), avec des seuils 4 fois plus hauts que ceux d'une adresse (80 écritures et 480 lectures par minute avec les valeurs par défaut). Les deux limiteurs sont deux instances du même port. La limite de l'adresse est consultée d'abord : si elle refuse, la limite du bloc n'est pas consommée, pour qu'une adresse qui insiste n'épuise pas le quota de ses voisins du même /48.
- **Les chemins pièges comptent dans la limite de débit**, mais pas dans le blocage des écritures : un piège répond toujours le même 404 qu'une adresse inconnue. Ils sont reconnus quelle que soit la casse, dans l'API comme dans Caddy (dont le matcher `path` ignore déjà la casse).
- **Caractères refusés dans les textes** : en plus des contrôles (Cc) et des demi-codets (Cs), les séparateurs de ligne et de paragraphe (Zl, Zp), l'usage privé (Co) et la mise en forme (Cf), sauf une liste blanche de ce qui sert vraiment : U+200C et U+200D (liants), U+200E et U+200F (marques de sens), U+E0020 à U+E007F (étiquettes des drapeaux régionaux). Les caractères bidirectionnels, de catégorie Cf, restent refusés. Les caractères non attribués (Cn) restent acceptés. Un texte obligatoire sans aucun caractère visible est refusé. Les adresses déjà enregistrées sont nettoyées par une migration de données (0003), car elles sont relues par leur constructeur.
- **Refus de droit** : une action qu'un rôle n'a jamais le droit de faire, depuis aucun statut de la table des transitions, lève `AccesRefuse` (403). Une action permise au rôle, mais pas depuis le statut actuel (un saut d'état), reste `TransitionInterdite` (409).

## Alternatives écartées
- **Bloquer tout le /48 dès que plusieurs /64 ont touché un piège** : plus efficace contre l'esquive du blocage, mais une règle de plus à écrire et à tester, et le risque de bloquer tout un opérateur ; la limite par /48 borne déjà les écritures.
- **Compter uniquement par /48** : un seuil commun ferait payer à chaque abonné d'un même /48 les excès de ses voisins.
- **Seuil du /48 égal à celui d'une adresse** : trop serré si plusieurs abonnés partagent un /48.
- **Refuser aussi les caractères non attribués (Cn)** : la base Unicode de Python ne connaît pas les emojis les plus récents ; les refuser bloquerait des saisies légitimes sur téléphone.
- **Refuser toute la catégorie Cf** : casserait les emojis composés, les drapeaux régionaux et l'écriture persane.
- **404 pour l'ouvrier qui valide** : le squelette n'a pas de cloisonnement, l'ouvrier voit déjà l'étape ; un 404 serait faux.
- **Garder le 409** : il dit à l'ouvrier que l'étape n'est pas dans le bon état, ce qui le trompe.

## Conséquences
- Un robot qui dispose d'un /48 n'écrit pas plus de 80 fois par minute au total.
- Risques résiduels assumés pour la démo :
  - des abonnés mobiles d'un même opérateur peuvent partager un /48 et se gêner au-delà du seuil ;
  - le blocage d'un piège ne vise qu'un /64 : un robot qui a un /48 change de /64 et continue d'écrire, dans la limite du /48 ;
  - un /48 peut encore remplir la liste des adresses bloquées (10 000 entrées) en une vingtaine de minutes, moins que la durée du blocage, et faire oublier les blocages les plus anciens.

  Ces points sont à revoir avec l'authentification de la phase 2.
- Un second compteur en mémoire, avec les hypothèses de l'ADR 0016 (un seul processus, état perdu au redémarrage).
- La migration 0003 est irréversible : les caractères retirés des adresses sont perdus, et un champ devenu vide vaut « À préciser ».
- Un client qui attendait un 409 pour l'ouvrier reçoit désormais un 403.
