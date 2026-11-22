// @vitest-environment node
// Preuves des garde-fous ESLint : un garde-fou n'est en place que lorsqu'on l'a vu échouer.
//
// Chaque fichier de `fixtures/` enfreint volontairement une règle. Ces fichiers forment un
// mini-projet (avec son `src/` et ses `tsconfig`), lu avec EXACTEMENT la configuration du vrai
// projet (`creerConfig`) : si une règle venait à être affaiblie ou retirée, un de ces tests
// passerait au rouge. Les fixtures sont exclues du lint normal (voir `eslint/creer-config.js`).
import { fileURLToPath } from 'node:url';

import { ESLint } from 'eslint';
import { beforeAll, describe, expect, it } from 'vitest';

import { creerConfig } from '../../eslint/creer-config.js';

const RACINE_FIXTURES = fileURLToPath(new URL('./fixtures', import.meta.url));
/** Le lint typé d'un mini-projet complet est lent au premier passage. */
const DELAI_LINT_MS = 180_000;

/** Une violation volontaire : le fichier qui l'enfreint et la règle attendue. */
type Cas = { readonly fichier: string; readonly regle: string; readonly raison: string };

const DEMO = 'src/features/demo';

const CAS_DE_VIOLATION: readonly Cas[] = [
  {
    fichier: `${DEMO}/pages/PageBoutonBrut.tsx`,
    regle: 'react/forbid-elements',
    raison: '<button> brut dans une page',
  },
  {
    fichier: `${DEMO}/components/ComposantAvecClassName.tsx`,
    regle: 'react/forbid-dom-props',
    raison: 'className sur un élément HTML',
  },
  {
    fichier: `${DEMO}/components/ComposantAvecClassName.tsx`,
    regle: 'react/forbid-component-props',
    raison: 'className sur un composant ui',
  },
  {
    fichier: `${DEMO}/pages/PageImportApi.tsx`,
    regle: 'boundaries/dependencies',
    raison: 'page qui importe src/api',
  },
  {
    fichier: `${DEMO}/services/AppelFetchDirect.ts`,
    regle: 'no-restricted-globals',
    raison: 'fetch hors de src/api',
  },
  {
    fichier: `${DEMO}/services/AppelFetchFenetre.ts`,
    regle: 'no-restricted-properties',
    raison: 'window.fetch hors de src/api',
  },
  {
    fichier: 'src/ui/CarteCouleurArbitraire.tsx',
    regle: 'no-restricted-syntax',
    raison: 'couleur et valeurs Tailwind arbitraires',
  },
  { fichier: `${DEMO}/services/cycleA.ts`, regle: 'import/no-cycle', raison: 'import circulaire' },
  {
    fichier: `${DEMO}/pages/PageRadix.tsx`,
    regle: 'no-restricted-imports',
    raison: 'Radix hors de src/ui',
  },
  {
    fichier: `${DEMO}/services/ImportOpenapiFetch.ts`,
    regle: 'no-restricted-imports',
    raison: 'openapi-fetch hors de src/api',
  },
  {
    fichier: 'src/features/autre/pages/PageAutre.tsx',
    regle: 'boundaries/dependencies',
    raison: 'features/A importe features/B',
  },
  {
    fichier: 'src/ui/ImporteFonctionnalite.tsx',
    regle: 'boundaries/dependencies',
    raison: 'ui importe une fonctionnalité',
  },
  {
    fichier: `${DEMO}/services/ServiceImporteUi.ts`,
    regle: 'boundaries/dependencies',
    raison: 'service qui importe ui',
  },
  {
    fichier: `${DEMO}/components/ComposantAppelleService.tsx`,
    regle: 'boundaries/dependencies',
    raison: 'composant qui appelle un service',
  },
  {
    fichier: `${DEMO}/services/UtiliseAny.ts`,
    regle: '@typescript-eslint/no-explicit-any',
    raison: 'any explicite',
  },
  {
    fichier: `${DEMO}/services/DesactivationParCommentaire.ts`,
    regle: '@typescript-eslint/no-explicit-any',
    raison: 'eslint-disable sans effet',
  },
  {
    fichier: `${DEMO}/services/AssertionDeType.ts`,
    regle: '@typescript-eslint/consistent-type-assertions',
    raison: 'assertion as',
  },
  {
    fichier: `${DEMO}/services/AssertionDeType.ts`,
    regle: '@typescript-eslint/no-non-null-assertion',
    raison: 'assertion non-null !',
  },
  { fichier: `${DEMO}/services/TropComplexe.ts`, regle: 'complexity', raison: 'complexité 9 > 8' },
  {
    fichier: `${DEMO}/services/TropDeParametres.ts`,
    regle: 'max-params',
    raison: '4 paramètres > 3',
  },
  {
    fichier: `${DEMO}/services/TropProfond.ts`,
    regle: 'max-depth',
    raison: 'imbrication de 4 blocs > 3',
  },
  {
    fichier: `${DEMO}/services/TropProfond.ts`,
    regle: 'max-nested-callbacks',
    raison: '4 callbacks imbriqués > 3',
  },
  {
    fichier: `${DEMO}/services/FonctionTropLongue.ts`,
    regle: 'max-lines-per-function',
    raison: 'fonction de plus de 60 lignes',
  },
  {
    fichier: `${DEMO}/services/FichierTropLong.ts`,
    regle: 'max-lines',
    raison: 'fichier de plus de 250 lignes',
  },
];

const FICHIERS_CONFORMES: readonly string[] = [
  `${DEMO}/pages/PageConforme.tsx`,
  `${DEMO}/components/CarteDemo.tsx`,
  `${DEMO}/services/useDemo.ts`,
  'src/ui/Texte.tsx',
  'src/ui/index.ts',
  'src/api/client.ts',
];

/** Identifiants des règles enfreintes, par fichier (chemin relatif au mini-projet). */
const reglesParFichier = new Map<string, string[]>();

beforeAll(async () => {
  const eslint = new ESLint({
    cwd: RACINE_FIXTURES,
    overrideConfigFile: true,
    overrideConfig: creerConfig({ racine: RACINE_FIXTURES }),
  });
  const resultats = await eslint.lintFiles(['src']);

  for (const resultat of resultats) {
    const fichier = resultat.filePath.slice(RACINE_FIXTURES.length + 1).replaceAll('\\', '/');
    const regles = resultat.messages.flatMap((message) =>
      message.ruleId === null ? [`erreur de syntaxe : ${message.message}`] : [message.ruleId],
    );
    reglesParFichier.set(fichier, regles);
  }
}, DELAI_LINT_MS);

describe('les garde-fous ESLint échouent sur une violation volontaire', () => {
  it.each(CAS_DE_VIOLATION)('$raison : $regle', ({ fichier, regle }) => {
    expect(reglesParFichier.get(fichier)).toContain(regle);
  });
});

describe('les fichiers conformes passent au vert avec les mêmes règles', () => {
  it.each(FICHIERS_CONFORMES)('%s', (fichier) => {
    expect(reglesParFichier.get(fichier)).toEqual([]);
  });
});
