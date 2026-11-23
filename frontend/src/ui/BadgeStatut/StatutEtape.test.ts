// Preuve de type : les statuts du badge sont exactement ceux du schéma OpenAPI généré. Si l'API
// ajoute ou retire un statut, `tsc -b` échoue ici au lieu de laisser un badge sans libellé.
import { expectTypeOf, it } from 'vitest';

import type { components } from '@/api/schema';

import type { StatutEtape } from './BadgeStatut';

it("a les mêmes statuts que l'API", () => {
  expectTypeOf<StatutEtape>().toEqualTypeOf<components['schemas']['EtapeReponse']['statut']>();
});
