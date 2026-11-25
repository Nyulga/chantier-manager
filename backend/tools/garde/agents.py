"""Familles de sous-agents que la garde traite à part, définies à un seul endroit.

Le test d'alignement compare ces listes aux fiches de `.claude/agents/` : un agent ajouté ou
renommé sans mise à jour de la garde fait échouer `just verifier`.
"""

# Ces agents vérifient sans rien modifier : les commandes d'écriture (`rm`, `sed -i`…) leur sont
# refusées en plus de l'écriture de fichiers.
VERIFICATEURS = ("revue", "conformite", "securite")

# Ces agents n'ont ni Edit ni Write : un appel d'écriture qui arrive quand même est refusé.
AGENTS_SANS_ECRITURE = (*VERIFICATEURS, "pentest", "backlog")
