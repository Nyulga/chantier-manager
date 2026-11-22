// Violation volontaire : un composant du design system qui importe une fonctionnalité.
import { useDemo } from '@/features/demo/services/useDemo';

export function ImporteFonctionnalite() {
  return <p>{useDemo()}</p>;
}
