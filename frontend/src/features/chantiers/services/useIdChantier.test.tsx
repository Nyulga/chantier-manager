// Tests du hook `useIdChantier` : l'identifiant vient de l'adresse, jamais d'une valeur de remplacement.
import { testerUseIdChantier } from '@/test/testerUseIdChantier';

import { useIdChantier } from './useIdChantier';

testerUseIdChantier(useIdChantier);
