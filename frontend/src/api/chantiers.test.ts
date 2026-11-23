// Tests de la conversion d'un chantier de l'API en résumé : la carte n'a besoin que de valeurs simples.
import { expect, it } from 'vitest';

import { chantierDeTest } from '@/test/chantierDeTest';

import { resumerChantier } from './chantiers';

it("met l'adresse à plat et ne garde que ce que la carte affiche", () => {
  const chantier = chantierDeTest({ etapes_a_valider: 2, en_retard: true, jours_restants: 4 });

  expect(resumerChantier(chantier)).toEqual({
    id: chantier.id,
    nom: 'Rénovation de la mairie',
    adresse: '12 rue des Lilas, 69003 Lyon',
    etapesValidees: 3,
    etapesTotal: 6,
    avancement: 50,
    etapesAValider: 2,
    echeance: '2026-09-30',
    joursRestants: 4,
    enRetard: true,
  });
});

it("ne laisse passer ni le budget ni le client : la carte n'en a pas besoin", () => {
  const resume = resumerChantier(chantierDeTest({ budget: '18450.00' }));

  expect(resume).not.toHaveProperty('budget');
  expect(resume).not.toHaveProperty('client');
});
