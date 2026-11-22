// Tests du formatage des dates : le format français JJ/MM/AAAA, sans effet de fuseau horaire.
import { expect, it } from 'vitest';

import { formaterDate } from './formaterDate';

it('écrit une date ISO au format français JJ/MM/AAAA', () => {
  expect(formaterDate('2026-03-07')).toBe('07/03/2026');
});

it('garde la date du jour même en fin d’année', () => {
  expect(formaterDate('2026-12-31')).toBe('31/12/2026');
});

it('renvoie le texte tel quel quand ce n’est pas une date ISO', () => {
  expect(formaterDate('bientôt')).toBe('bientôt');
});
