// Page d'accueil de l'application : nom du produit et emplacement de l'état de l'API.
import { Page, Texte, Titre } from '@/ui';

/**
 * Écran affiché à l'adresse `/`.
 *
 * L'emplacement « État de l'API » est volontairement statique pour l'instant : un service
 * (hook TanStack Query) l'alimentera avec la réponse de `/api/health` une fois le client
 * généré disponible. La page n'appelle jamais l'API directement.
 */
export function PageAccueil() {
  return (
    <Page>
      <Titre niveau={1}>Chantier Manager</Titre>
      <Texte variante="secondaire">État de l’API : pas encore vérifié.</Texte>
    </Page>
  );
}
