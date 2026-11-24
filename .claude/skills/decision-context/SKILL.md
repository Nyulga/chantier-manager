---
name: decision-context
description: Lit et rédige les décisions d'architecture de chantier-manager (ADR) dans docs/adr/. À utiliser avant de proposer un choix d'architecture, de bibliothèque, de structure ou de process, et dès qu'une décision est prise en écartant d'autres options.
---

# decision-context · les décisions du projet

Les décisions d'architecture vivent dans `docs/adr/` : un fichier par décision, commité avec le code, et un index dans `docs/adr/README.md`. `intent.md` reste la source de vérité : un ADR le précise, il ne le contredit jamais.

## Avant d'agir

1. Lis `docs/adr/README.md`, puis les ADR qui touchent ta tâche.
2. Ne propose pas une option qu'un ADR « accepté » a écartée (section « Alternatives écartées »). Si elle te semble meilleure aujourd'hui, dis-le à l'utilisateur et demande-lui d'abord.
3. Deux ADR acceptés se contredisent, ou un ADR contredit `intent.md` : signale-le à l'utilisateur, ne tranche pas seul.

## Quand écrire un ADR

Quand un choix structurant est pris (architecture, bibliothèque, structure du code, process) et que d'autres options ont été écartées. Une simple correction ou un détail d'implémentation n'en demande pas.

## Format

Fichier : `docs/adr/NNNN-<slug>.md`, sur quatre chiffres, au numéro qui suit le dernier. Le slug est en français, sans accents, avec des tirets.

```markdown
# ADR NNNN – <Titre>

- **Statut** : accepté
- **Date** : AAAA-MM-JJ (lot NN, ou « hors lot »)

## Contexte
Le problème et les contraintes du moment.

## Décision
Ce qui est retenu, et pourquoi.

## Alternatives écartées
- **<Option>** : écartée parce que <raison>.

## Conséquences
Ce que ça change, en bien comme en mal.
```

Ajoute ensuite une ligne à la table de `docs/adr/README.md`.

## Les règles

- **Montrer avant d'écrire** : tu rédiges l'ADR, tu le montres à l'utilisateur, et tu ne l'écris qu'avec son accord.
- **Un ADR est immuable.** Si la décision change, on écrit un nouvel ADR. L'ancien passe au statut « remplacé par l'ADR NNNN », dans son fichier et dans l'index ; c'est la seule modification permise.
- **« Alternatives écartées » est toujours rempli** : c'est ce qui évite de reproposer un choix déjà rejeté.
- **Rien de sensible** : le dépôt est public. Ni secret, ni donnée réelle, ni détail du serveur (chemins, adresses, état du pare-feu).
- Rédaction en français, en phrases complètes, comme le reste de la documentation.
