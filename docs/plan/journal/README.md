# Journal des lots

Un fichier par lot, `lot-NN.md`, tenu par le coordinateur pendant le lot (skill [`lot`](../../../.claude/skills/lot/SKILL.md)).

Pour chaque étape, le journal consigne :
- l'agent qui l'a réalisée, avec son modèle et son effort ;
- les tests ajoutés, chacun avec le critère qu'il prouve ;
- un extrait de la **sortie rouge** (les tests échouent avant le code), puis de la **sortie verte** ;
- le commit correspondant.

En fin de lot, il ajoute les verdicts de `revue`, `conformite` et `securite`, ainsi que le lien de la CI.

Ce journal sert de preuve du TDD et alimente le corps de la PR. Il ne contient jamais de secret ni de donnée réelle.
