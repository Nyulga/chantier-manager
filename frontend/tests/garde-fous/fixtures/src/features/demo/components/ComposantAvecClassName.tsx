// Violation volontaire : la prop className sur un élément HTML et sur un composant ui,
// dans un composant de fonctionnalité.
import { Texte } from '@/ui';

export function ComposantAvecClassName() {
  return (
    <div className="p-4">
      <Texte className="text-fg">Texte</Texte>
    </div>
  );
}
