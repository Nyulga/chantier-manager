"""Garde des sous-agents (ADR 0017), appelée par le hook `PreToolUse` du projet.

Chaque sous-agent n'écrit que dans les dossiers de sa couche, aucun ne modifie la configuration de
Claude Code ni la garde elle-même, et aucun ne change l'état du dépôt git. Le point d'entrée est
`tools/garde_agents.py` ; ce paquet contient la logique, découpée par responsabilité :
- `chemins` compare les chemins ;
- `droits` porte la table des droits d'écriture ;
- `commandes` analyse les commandes Bash ;
- `protocole` lit l'appel envoyé par Claude Code et forme la réponse ;
- `refus` rédige la raison renvoyée à l'agent.

C'est une barrière contre les erreurs de bonne foi, pas contre la malveillance : une écriture faite
par un autre moyen (`python -c`, redirection `>`, script écrit puis lancé) n'est pas vue.
"""
