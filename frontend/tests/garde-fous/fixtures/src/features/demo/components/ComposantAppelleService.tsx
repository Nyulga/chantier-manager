// Violation volontaire : un composant qui appelle un service au lieu de tout recevoir par ses
// props (seuls les types des services sont importables).
import { Texte } from '@/ui';

import { useDemo } from '../services/useDemo';

export function ComposantAppelleService() {
  return <Texte>{useDemo()}</Texte>;
}
