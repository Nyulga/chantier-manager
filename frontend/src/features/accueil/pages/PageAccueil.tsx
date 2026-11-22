// Page d'accueil de l'application : nom du produit et état de l'API.
import { Page, Texte, Titre } from '@/ui';

import { useEtatApi } from '../services/useEtatApi';

/**
 * Écran affiché à l'adresse `/`.
 *
 * L'état de l'API vient du hook `useEtatApi` : la page n'appelle jamais l'API elle-même.
 */
export function PageAccueil() {
  const { isPending, isError } = useEtatApi();

  let etat = 'disponible.';
  if (isPending) {
    etat = 'vérification en cours…';
  } else if (isError) {
    etat = 'indisponible.';
  }

  return (
    <Page>
      <Titre niveau={1}>Chantier Manager</Titre>
      <Texte variante="secondaire">{`État de l’API : ${etat}`}</Texte>
    </Page>
  );
}
