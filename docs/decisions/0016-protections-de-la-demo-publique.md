# ADR 0016 – Protections de la démo publique

- **Statut** : accepté (squelette). Il complète l'ADR 0008 (contrat d'erreur) et l'ADR 0015 (déploiement).
- **Date** : 2026-11-24 (lot S6).

## Contexte
La démo du squelette est publique et ouverte en écriture, sans authentification (ADR 0015). N'importe qui peut créer des chantiers et des étapes. Le premier test d'intrusion (constat M1) a montré que les protections existaient seulement dans le Caddy du serveur : la copie locale, les tests et le pentest local ne les voyaient pas, et une erreur de configuration du proxy les aurait toutes supprimées d'un coup.

Il fallait donc limiter ce qu'un visiteur ou un robot peut faire, sans compte et sans remettre la démo à zéro.

## Décision
- **Les protections vivent dans l'application, en plus du proxy** :
  - en-têtes de sécurité ;
  - taille maximale du corps des requêtes ;
  - liste des noms d'hôte acceptés ;
  - documentation de l'API fermée par défaut ;
  - refus des caractères de contrôle et des caractères bidirectionnels dans les textes (domaine).

  Le proxy garde les mêmes protections (`deploy/protections.caddy`), partagées par la copie locale et la production.
- **Limite de débit et blocage par adresse, en mémoire** :
  - 20 écritures et 120 lectures par minute et par adresse, en fenêtre glissante ; une adresse IPv6 compte pour son bloc /64, celui d'un abonné, pour qu'un robot ne puisse pas changer d'adresse à chaque requête ;
  - une adresse qui touche une fausse adresse piège (`/wp-admin`, `/.env`, `/.git/…`) ou remplit le champ piège d'un formulaire perd le droit d'écrire pendant une heure.

  Ces compteurs vivent en mémoire, d'où **un seul processus API** (`--workers 1`). Les ports `LimiteurDebit` et `ListeAdressesBloquees` n'ont qu'une implémentation pendant le squelette : c'est une **dérogation écrite au principe L** de la règle 00, qui demande deux implémentations par port.
- **Un piège ne bloque que les requêtes qui ne viennent pas d'un navigateur** (en-tête `Sec-Fetch-Site` absent), et le champ piège n'est examiné que dans un corps JSON. Sans cela, un site tiers pourrait faire bloquer un visiteur en lui faisant charger `/wp-admin` à son insu.
- **L'adresse du client est donnée par le proxy**, qui la force (`X-Forwarded-For` réécrit avec l'adresse réelle). L'API ne fait confiance à cet en-tête que parce qu'elle n'est joignable que par le proxy (ADR 0015).
- **Plafonds de volume** : 100 chantiers, 30 étapes par chantier et 20 transitions par étape. La validation, qui mène à un statut final, n'est pas soumise à ce dernier plafond : une étape pleine peut toujours être validée par son chef, et son historique ne dépasse jamais 21 entrées. Un plafond atteint renvoie **409 « plafond atteint »**, au format RFC 9457. Ce cas s'ajoute à la liste des erreurs de l'ADR 0008. Les créations passent l'une après l'autre dans la base, pour qu'aucune course ne fasse dépasser un plafond.

## Alternatives écartées
- **Redis ou la base pour le limiteur** : un service de plus, ou une écriture en base à chaque requête, pour un seul conteneur API. C'est trop lourd pour la démo.
- **Protections seulement dans Caddy** : c'est la situation du constat M1. Les tests et la copie locale ne les voyaient pas.
- **Remettre la démo à zéro régulièrement** : refusé par le propriétaire, qui garde les données saisies.
- **fail2ban sur le serveur** : il relève du durcissement du serveur, reporté au lot 08.

## Conséquences
- **En bien** : les protections sont testées comme le reste du code, et la copie locale se comporte comme la production.
- **En mal** :
  - un redémarrage de l'API vide les compteurs et la liste des adresses bloquées ;
  - plusieurs processus ou plusieurs conteneurs demanderont un limiteur partagé, donc un nouvel ADR ;
  - des personnes derrière une même adresse (entreprise, réseau mobile) partagent le même quota ;
  - la dérogation au principe L prend fin avec le squelette : la phase 2 doit fournir une seconde implémentation ou revoir ce choix.
