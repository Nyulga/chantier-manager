// Tests du formatage du délai avant l'échéance : « J-n », « Aujourd'hui » ou le retard en jours.
import { expect, it } from 'vitest';

import { formaterDelai } from './formaterDelai';

it("écrit le compte à rebours « J-n » avant l'échéance", () => {
  expect(formaterDelai({ joursRestants: 54, enRetard: false })).toBe('J-54');
});

it("écrit « Aujourd'hui » le jour même de l'échéance", () => {
  expect(formaterDelai({ joursRestants: 0, enRetard: false })).toBe("Aujourd'hui");
});

it('écrit le retard au pluriel', () => {
  expect(formaterDelai({ joursRestants: 4, enRetard: true })).toBe('En retard de 4 jours');
});

it("écrit le retard d'un jour au singulier", () => {
  expect(formaterDelai({ joursRestants: 1, enRetard: true })).toBe('En retard de 1 jour');
});
