// Tests du hook `useIdChantier` des étapes : même contrat que celui des chantiers.
import { testerUseIdChantier } from '@/test/testerUseIdChantier';

import { useIdChantier } from './useIdChantier';

testerUseIdChantier(useIdChantier);
