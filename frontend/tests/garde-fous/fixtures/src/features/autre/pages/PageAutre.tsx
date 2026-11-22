// Violation volontaire : une fonctionnalité (autre) importe une autre fonctionnalité (demo).
import { Texte } from '@/ui';

import { useDemo } from '../../demo/services/useDemo';

export function PageAutre() {
  return <Texte>{useDemo()}</Texte>;
}
