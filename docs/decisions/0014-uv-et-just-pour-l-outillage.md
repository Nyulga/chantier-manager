# ADR 0014 – uv pour le Python et just pour les commandes

- **Statut** : accepté
- **Date** : 2026-11-24 (hors lot). Le choix est fait depuis le lot S1 (`intent.md`, section outils). Cet ADR le consigne après coup.

## Contexte
Le projet se développe sous Windows et tourne sous Linux (CI et serveur). Il faut :
- installer les dépendances Python aux versions exactes, partout pareil ;
- lancer les mêmes commandes (vérifier, tester, générer le client) sur le poste, en CI et dans les hooks git, sans les recopier dans chaque outil.

## Décision
- **uv** gère le Python du backend : la version de Python, l'environnement virtuel et les dépendances.
  - Les versions exactes sont verrouillées dans `backend/uv.lock`.
  - L'installation se fait toujours avec `uv sync --locked`, sur le poste, en CI et dans l'image Docker : elle échoue si le verrou ne correspond plus à `pyproject.toml`.
- **just** rassemble toutes les commandes du projet dans le `justfile` de la racine : `installer`, `lancer`, `verifier`, `e2e`, `client`, `doublons`, `hooks`…
  - La même recette marche sous Windows (PowerShell) et sous Linux.
  - `just verifier` est la porte d'entrée de la CI : ce qui passe en local passe en CI.

## Alternatives écartées
- **pip et requirements.txt** : il n'y a pas de verrou fiable des dépendances indirectes, et l'installation est lente.
- **Poetry** : il fait le même travail que uv, mais plus lentement, et il ne gère pas la version de Python.
- **make** : il est absent par défaut sous Windows, et sa syntaxe (tabulations, variables) piège facilement.
- **Scripts npm (`package.json`)** : ils mélangeraient les commandes du backend dans un fichier du frontend.
- **Scripts PowerShell ou bash séparés** : il faudrait deux versions de chaque commande, une par système.

## Conséquences
- **En bien** : une seule commande à retenir (`just verifier`), des installations rapides et identiques, et la CI ne fait rien de plus que ce qu'on lance soi-même.
- **En mal** : deux outils à installer sur le poste (via winget sous Windows). Si le shell ne les trouve pas, il faut rafraîchir le `PATH`.
