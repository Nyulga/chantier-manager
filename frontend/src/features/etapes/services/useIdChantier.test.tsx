// Tests du hook `useIdChantier` : le paramètre de route lu, et l'erreur s'il manque.
import { verifierLectureIdChantier } from '@/test/verifierLectureIdChantier';

import { useIdChantier } from './useIdChantier';

verifierLectureIdChantier(useIdChantier);
