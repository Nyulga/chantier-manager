// Violation volontaire : un fichier de production qui importe une aide de test (src/test).
import { Texte } from '@/ui';

import { DONNEE_DE_TEST } from '@/test/aideDeTest';

export function PageImporteAideDeTest() {
  return <Texte>{DONNEE_DE_TEST}</Texte>;
}
