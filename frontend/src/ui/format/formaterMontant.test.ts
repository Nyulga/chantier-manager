// Tests du formatage des montants : euros à la française, à partir de la chaîne décimale de l'API.
import { expect, it } from 'vitest';

import { formaterMontant } from './formaterMontant';

/** Intl sépare les milliers et l'euro par des espaces insécables : on les ramène à une espace simple. */
const normaliser = (texte: string) => texte.replace(/\s/g, ' ');

it('écrit un montant en euros avec deux décimales et une virgule', () => {
  expect(normaliser(formaterMontant('18450.00'))).toBe('18 450,00 €');
});

it('garde les centimes de la chaîne reçue', () => {
  expect(normaliser(formaterMontant('125000.50'))).toBe('125 000,50 €');
});

it('ne perd pas de précision sur un grand montant', () => {
  expect(normaliser(formaterMontant('12345678901234567.89'))).toBe('12 345 678 901 234 567,89 €');
});

it("rend tel quel un texte qui n'est pas un montant décimal", () => {
  expect(formaterMontant('sur devis')).toBe('sur devis');
});
