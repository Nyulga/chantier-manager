---
name: git-conventional
description: Écrit et vérifie les messages de commit de chantier-manager au format Conventional Commits, avec les portées du projet (lot, couche ou dossier). À utiliser avant chaque commit, ou quand on demande un message de commit.
---

# git-conventional · des commits lisibles

## Le format

```
<type>[(portée)]: <description>

[corps, facultatif]

[pied, facultatif : BREAKING CHANGE: …]
```

## Les types

| Type | Pour |
|---|---|
| `feat` | une fonctionnalité |
| `fix` | une correction de bug |
| `docs` | la documentation seule (ADR, règles, plans, journaux) |
| `style` | la mise en forme, sans changer le comportement |
| `refactor` | une réécriture, sans changer le comportement |
| `perf` | une amélioration de performance |
| `test` | des tests ajoutés ou modifiés |
| `build` | le build ou les dépendances |
| `ci` | la configuration de la CI |
| `chore` | la maintenance, l'outillage |
| `revert` | l'annulation d'un commit |

## Les portées du projet

**Pendant un lot, la portée est toujours le lot** (skill `lot`) : `feat(lot-03): …`, `fix(lot-S6): …`, `docs(lot-05): clôture du lot`. Cela permet de retrouver tous les commits d'un lot.

**Hors lot, la portée est la couche ou le dossier touché.** On la choisit dans cette liste :

| Portée | Ce qu'elle couvre |
|---|---|
| `domain` | `backend/app/*/domain/` |
| `application` | `backend/app/*/application/` |
| `infrastructure` | `backend/app/*/infrastructure/` |
| `api` | `backend/app/*/api/` |
| `composition` | `backend/app/main.py`, `backend/app/composition/` |
| `shared` | `backend/app/shared/` |
| `migrations` | `backend/migrations/` |
| `outils` | `backend/tools/` |
| `frontend` | `frontend/src/` hors `ui` |
| `ui` | `frontend/src/ui/` (design system Balise) |
| `e2e` | `frontend/e2e/` |
| `tests` | `backend/tests/`, `frontend/src/test/` |
| `deploy` | `deploy/` |
| `ci` | `.github/` |
| `decisions` | `docs/decisions/` |
| `plan` | `docs/plan/` |
| `regles` | `.claude/rules/` |
| `agents` | `.claude/agents/`, `.claude/skills/` |
| `deps` | dépendances (`pyproject.toml`, `uv.lock`, `package.json`, `pnpm-lock.yaml`) |

Un changement qui touche plusieurs couches pour un seul but : la couche principale, ou pas de portée. Un nom de module métier (`chantiers`, `etapes`) peut servir de portée quand c'est plus clair que la couche.

## Les règles

- Le type est l'un de ceux du tableau.
- La portée est facultative, en minuscules : lettres, chiffres, tirets. Elle vient de la liste ci-dessus.
- La description est **en français**, commence par une minuscule, à l'impératif présent ou au présent (« ajoute », « corrige »), sans point final, 100 caractères au plus.
- Le corps explique le **pourquoi**, en français, en phrases complètes. Il ne contient aucun secret, aucune donnée réelle et aucun détail du serveur : le dépôt est public.
- Le message se termine par la ligne d'attribution demandée par la session.
- Un changement qui casse la compatibilité : `!` après le type (`feat!:`) et un pied `BREAKING CHANGE:` qui dit quoi faire.
- Un commit = un changement. Deux changements sans rapport : deux commits.
- Avant de commiter : vérifier que la branche est `dev`.

## Exemples

```
feat(lot-03): domaine utilisateur et politique de mot de passe
fix(frontend): garde les données fraîches 30 s pour ne plus tout relire à chaque écran
docs(decisions): ADR 0016, limite de débit de la démo
chore(outils): contrôle les désactivations de règles en Python
ci: épingle l'action setup-uv par SHA
build(deps): met à jour fastapi en 0.140
```

Refusés : `Ajout de la page` (pas de type), `feat ajoute la page` (pas de deux-points), `feat(UI): ajoute la page` (portée en majuscules), `feat: Ajoute la page.` (majuscule et point final), `feat(backend): …` (portée hors de la liste).
