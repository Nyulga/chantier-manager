// Tests de la règle de nouvelle tentative des requêtes : une réponse définitive de l'API n'est jamais rejouée.
import { expect, it } from 'vitest';

import { ErreurApi } from './erreurApi';
import { reessayerRequete } from './reessai';

it.each([403, 404, 422])(
  "ne rejoue jamais une requête refusée par l'API (%i) : la réponse ne changera pas",
  (statut) => {
    expect(reessayerRequete(0, new ErreurApi('Refusé.', statut))).toBe(false);
  },
);

it("rejoue une panne du serveur ou du réseau, jusqu'à trois fois", () => {
  const panneReseau = new ErreurApi('Le serveur ne répond pas.');
  const panneServeur = new ErreurApi('Service indisponible.', 503);

  expect(reessayerRequete(0, panneReseau)).toBe(true);
  expect(reessayerRequete(2, panneServeur)).toBe(true);
  expect(reessayerRequete(3, panneServeur)).toBe(false);
});
