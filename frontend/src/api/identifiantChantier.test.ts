// Tests de la lecture de l'identifiant du chantier : il vient de l'adresse, jamais d'une valeur de remplacement.
import { expect, it } from 'vitest';

import { lireIdentifiantChantier } from './identifiantChantier';

it("renvoie l'identifiant présent dans l'adresse", () => {
  expect(lireIdentifiantChantier('abc')).toBe('abc');
});

it("refuse une route sans identifiant, plutôt que d'envoyer une requête vide", () => {
  expect(() => lireIdentifiantChantier(undefined)).toThrow(/identifiant/);
});
