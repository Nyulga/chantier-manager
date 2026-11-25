# ADR 0017 – Garde-fous des sous-agents

- **Statut** : accepté
- **Date** : 2026-11-25 (lot S7)

## Contexte
Le code est écrit par des sous-agents, un par couche (`dev-metier`, `dev-donnees`, `dev-api`, `dev-frontend`, `dev-socle`), et seul le coordinateur commite (skill `lot`). Jusqu'au lot S6, ce partage n'était imposé que par les consignes des agents et par la relecture en fin de lot. Pendant le lot S6, un comptage SQL a failli être confié à `dev-metier`. Le propriétaire veut que ce genre d'écart soit refusé automatiquement (issue #46).

## Décision
- **Un hook `PreToolUse` de projet** (`.claude/settings.json`, suivi par Git) appelle `backend/tools/garde_agents.py` avant chaque `Edit`, `Write` et `Bash`. Ce point d'entrée délègue au paquet `backend/tools/garde/`, découpé par responsabilité (chemins, droits, commandes, protocole). Le script lit le nom du sous-agent (`agent_type`) dans l'entrée du hook.
- **La session principale n'est pas concernée** : sans nom d'agent, tout est permis, avant toute autre vérification. Le coordinateur doit pouvoir commiter, et réparer la garde si elle tombe en panne.
- **Chaque agent développeur n'écrit que dans les dossiers de sa couche.** La table des droits suit les règles 01 à 07 et 09, et un test vérifie qu'elle reste alignée sur les fiches des agents. Un sous-agent qui n'est pas dans la table n'écrit pas dans le dépôt.
- **Aucun sous-agent ne modifie la configuration de Claude Code** (`.claude/` et `.claude.json`, dans le dépôt comme dans le dossier personnel) **ni la garde elle-même**, pour qu'aucun agent ne puisse élargir ses propres droits. Une correction de la garde est faite par le coordinateur, avec l'accord du propriétaire. Les formes de chemin que Windows ramène à un autre fichier (`x.py.`, `x.py::$DATA`, chemins réseau) sont refusées.
- **Pour git, une liste blanche** : un sous-agent ne lance que des sous-commandes qui lisent le dépôt (`status`, `diff`, `log`, `show`…). Toute autre sous-commande revient au coordinateur, comme `gh pr checkout` et `gh pr merge`. Les vérificateurs `revue`, `conformite` et `securite` ne lancent pas non plus `rm`, `mv`, `cp`, `tee` ni `sed -i`.
- **En cas de doute, la garde bloque** : une entrée illisible, une erreur inattendue, un Python antérieur à 3.13 ou un paquet impossible à charger donnent le code de sortie 2, le seul que Claude Code lit comme un blocage. La commande du hook se termine par `|| exit 2` pour le cas où Python lui-même est introuvable.
- **Le script n'utilise que la bibliothèque standard**, lancé par `python -I` sans uv, pour ne pas ralentir chaque action. Il est testé par pytest dans `just verifier`, comme les autres outils.

## Alternatives écartées
- **Des hooks dans l'en-tête de chaque fichier d'agent** : dix fichiers à tenir alignés, et la documentation ne garantit pas que `$CLAUDE_PROJECT_DIR` y est disponible. Un seul hook de projet, avec une seule table, est plus simple à relire et à tester.
- **Les consignes et la relecture seules** : c'était la situation du lot S6. L'écart n'est vu qu'à la fin du lot, quand le travail est déjà fait.
- **Retirer `Bash` aux agents développeurs** : ils en ont besoin pour lancer les tests en TDD.
- **Une liste noire de commandes git** : la première version du lot S7 en avait une, et la revue a trouvé une dizaine de commandes qui modifiaient le dépôt sans y figurer (`pull`, `add`, `config`…).

## Conséquences
- **En bien** : un agent qui sort de sa couche est arrêté au moment de l'écriture, avec une raison qui lui dit de le signaler au coordinateur. La table des droits est testée.
- **En mal** :
  - ce n'est pas une barrière absolue : une écriture faite par une commande du terminal (`python -c`, une redirection `>`) n'est pas vue. Au lot S7 lui-même, `dev-socle` a ainsi modifié puis restauré le client généré, qui ne lui appartient pas, pour tester sa recette. Le garde-fou arrête les erreurs de bonne foi, la relecture reste nécessaire ;
  - si Python est introuvable sur le poste, le hook bloque tous les appels `Edit`, `Write` et `Bash`, coordinateur compris : il faut réparer l'installation de Python, ou retirer le hook à la main ;
  - un nouveau dossier ou un nouvel agent demande de mettre la table à jour, par le coordinateur ;
  - quelques faux positifs (`git stash list`, un heredoc qui contient une commande git) et les limites restantes sont suivis dans les issues #78 à #80.
