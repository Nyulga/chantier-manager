// Tests du formatage de la date du jour : jour de la semaine, jour, mois en lettres et année.
import { expect, it } from 'vitest';

import { formaterDateLongue } from './formaterDateLongue';

it('écrit la date en toutes lettres, en français', () => {
  expect(formaterDateLongue(new Date(2026, 10, 22))).toBe('dimanche 22 novembre 2026');
});

it("écrit « 1er » le premier du mois, comme le veut l'usage français", () => {
  expect(formaterDateLongue(new Date(2026, 11, 1))).toBe('mardi 1er décembre 2026');
});
