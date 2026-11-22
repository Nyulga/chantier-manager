// Violation volontaire : une page qui importe directement src/api au lieu de passer par services.
import { Texte } from '@/ui';

import { client } from '@/api/client';

export function PageImportApi() {
  return <Texte>{client.obtenirEtat()}</Texte>;
}
