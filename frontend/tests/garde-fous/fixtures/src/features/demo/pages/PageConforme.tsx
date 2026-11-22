// Fixture conforme : une page qui utilise services, components et ui, sans rien d'interdit.
import { Texte } from '@/ui';

import { CarteDemo } from '../components/CarteDemo';
import { useDemo } from '../services/useDemo';

export function PageConforme() {
  return (
    <>
      <CarteDemo titre="Titre" />
      <Texte>{useDemo()}</Texte>
    </>
  );
}
