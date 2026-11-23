// Tests du hook `useChantiers` du tableau de bord : il lit la même liste que celui des chantiers (testé avec lui), avec la même règle de nouvelle tentative.
import { installerServeurApi } from '@/test/serveurApiSimule';
import { testerReessai } from '@/test/testerReessai';

import { useChantiers } from './useChantiers';

const serveur = installerServeurApi();

testerReessai({
  serveur,
  chemin: '/api/chantiers',
  corps: [],
  utiliser: useChantiers,
});
