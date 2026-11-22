// Fixture conforme : un composant de fonctionnalité, fait uniquement de composants ui.
import { Texte } from '@/ui';

export function CarteDemo({ titre }: { readonly titre: string }) {
  return <Texte>{titre}</Texte>;
}
