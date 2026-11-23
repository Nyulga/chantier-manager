// Tests du formatage d'un moment (date et heure) : relatif pour aujourd'hui et hier, sinon absolu.
import { expect, it } from 'vitest';

import { formaterMoment } from './formaterMoment';

/**
 * Dimanche 22 novembre 2026, 10 h 00, à l'heure locale. Les moments testés sont aussi construits
 * à l'heure locale puis écrits en ISO UTC, comme l'API : le test ne dépend pas du fuseau.
 */
const MAINTENANT = new Date(2026, 10, 22, 10, 0);

it("écrit « aujourd'hui à HH:MM » pour un moment du jour", () => {
  expect(formaterMoment(new Date(2026, 10, 22, 8, 5).toISOString(), MAINTENANT)).toBe(
    "aujourd'hui à 08:05",
  );
});

it('écrit « hier à HH:MM » pour un moment de la veille, même tard le soir', () => {
  expect(formaterMoment(new Date(2026, 10, 21, 23, 59).toISOString(), MAINTENANT)).toBe(
    'hier à 23:59',
  );
});

it("écrit la date complète au-delà d'hier", () => {
  expect(formaterMoment(new Date(2026, 10, 20, 17, 42).toISOString(), MAINTENANT)).toBe(
    'le 20/11/2026 à 17:42',
  );
});

it("renvoie le texte tel quel quand ce n'est pas une date valide", () => {
  expect(formaterMoment('bientôt', MAINTENANT)).toBe('bientôt');
});
