// Tests de la règle de nouvelle tentative des requêtes : une erreur 403 n'est jamais rejouée.
import { expect, it } from 'vitest';

import { AccesRefuseError } from './erreurApi';
import { reessayerRequete } from './reessai';

it('ne rejoue jamais une requête refusée par l’API (403) : la réponse ne changera pas', () => {
  expect(reessayerRequete(0, new AccesRefuseError('Action réservée à un chef.'))).toBe(false);
});

it('rejoue une autre erreur, jusqu’à trois fois', () => {
  const panne = new Error('Le service est indisponible.');

  expect(reessayerRequete(0, panne)).toBe(true);
  expect(reessayerRequete(2, panne)).toBe(true);
  expect(reessayerRequete(3, panne)).toBe(false);
});
