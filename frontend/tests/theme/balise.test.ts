// @vitest-environment node
// Vérifie que le thème Tailwind (`src/ui/theme/balise.css`) reprend fidèlement les tokens de
// `docs/design-system.md` : couleurs claires et sombres, statuts d'étape, polices, rayons.
import { readFileSync } from 'node:fs';

import { describe, expect, it } from 'vitest';

const CSS = readFileSync(new URL('../../src/ui/theme/balise.css', import.meta.url), 'utf8');
/** Bloc `@theme` (thème clair) et bloc sombre : le CSS est coupé au début du thème sombre. */
const [BLOC_CLAIR = '', BLOC_SOMBRE = ''] = CSS.split('@media (prefers-color-scheme: dark)');

const COULEURS_CLAIRES: Readonly<Record<string, string>> = {
  bg: '#f1f0ec',
  surface: '#ffffff',
  fg: '#1f2124',
  muted: '#5a5d62',
  line: '#d6d4ce',
  'line-soft': '#ebe9e4',
  accent: '#f2a900',
  'on-accent': '#1f2124',
  'accent-ink': '#855600',
  'accent-soft': '#fff8e6',
  danger: '#b42318',
  'danger-soft': '#fbe4e1',
  'statut-a-faire-fond': '#e7e6e2',
  'statut-a-faire-texte': '#3d4045',
  'statut-en-cours-fond': '#dde8f6',
  'statut-en-cours-texte': '#1d4f8c',
  'statut-a-valider-fond': '#f2a900',
  'statut-a-valider-texte': '#1f2124',
  'statut-validee-fond': '#dcefe1',
  'statut-validee-texte': '#1c6b34',
};

/** Le design system ne définit pas `line-soft` en sombre : il est absent de cette table. */
const COULEURS_SOMBRES: Readonly<Record<string, string>> = {
  bg: '#17191c',
  surface: '#202327',
  fg: '#ecebe7',
  muted: '#a4a7ac',
  line: '#353940',
  accent: '#f5b521',
  'accent-ink': '#f5b521',
  'on-accent': '#17191c',
  'accent-soft': '#2a2412',
  danger: '#f0716a',
  'danger-soft': '#3a1d1b',
  'statut-a-faire-fond': '#2c2f34',
  'statut-a-faire-texte': '#c9cbcf',
  'statut-en-cours-fond': '#1d3352',
  'statut-en-cours-texte': '#9cc3f5',
  'statut-a-valider-fond': '#f5b521',
  'statut-a-valider-texte': '#17191c',
  'statut-validee-fond': '#183823',
  'statut-validee-texte': '#8fd6a4',
};

describe('couleurs du thème clair', () => {
  it.each(Object.entries(COULEURS_CLAIRES))('--color-%s vaut %s', (nom, valeur) => {
    expect(BLOC_CLAIR).toContain(`--color-${nom}: ${valeur};`);
  });
});

describe('couleurs du thème sombre', () => {
  it.each(Object.entries(COULEURS_SOMBRES))('--color-%s vaut %s', (nom, valeur) => {
    expect(BLOC_SOMBRE).toContain(`--color-${nom}: ${valeur};`);
  });
});

describe('typographie, formes et espacements', () => {
  it.each([
    '--font-sans: ',
    '--font-mono: ',
    '--radius-controle: 0.25rem;',
    '--radius-badge: 0.375rem;',
    '--radius-avatar: 50%;',
    '--spacing-10: 2.5rem;',
    '--shadow-*: initial;',
    '--color-*: initial;',
  ])('le thème contient %s', (declaration) => {
    expect(BLOC_CLAIR).toContain(declaration);
  });

  it("charge Archivo avec l'axe de largeur et IBM Plex Mono depuis les paquets locaux", () => {
    expect(CSS).toContain('@fontsource-variable/archivo/wdth.css');
    expect(CSS).toContain('@fontsource/ibm-plex-mono/');
    expect(CSS).not.toContain('fonts.googleapis.com');
  });

  it('rend le titre condensé à 72 %, graisse 800, en majuscules', () => {
    expect(CSS).toMatch(
      /@utility titre-balise \{[^}]*font-stretch: 72%;[^}]*font-weight: 800;[^}]*uppercase/s,
    );
  });
});
