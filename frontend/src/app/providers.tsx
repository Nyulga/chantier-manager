// Fournisseurs globaux de l'application : requêtes serveur (TanStack Query) et routage.
// Aucun store global : l'état serveur vit dans TanStack Query, l'état local dans les composants.
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useState, type ReactNode } from 'react';
import { BrowserRouter } from 'react-router';

/**
 * Durée pendant laquelle une donnée lue est considérée comme fraîche : 30 secondes.
 *
 * Par défaut, TanStack Query la juge périmée aussitôt et la relit à chaque affichage d'un écran :
 * une simple navigation relançait alors toutes les requêtes, même celles reçues deux secondes plus
 * tôt. Avec ce délai, une navigation ne recharge plus ce qui vient d'arriver. Les actions de
 * l'utilisateur ne risquent pas de montrer une donnée périmée : elles invalident ce qu'elles
 * changent (`src/api/rafraichissement.ts`), et le changement de profil vide tout le cache. Les
 * actions des autres utilisateurs apparaissent au plus 30 secondes plus tard, ou dès le retour sur
 * l'onglet (`refetchOnWindowFocus` reste actif). Aucune règle métier ici : c'est un réglage de cache.
 */
const DUREE_FRAICHEUR_DONNEES = 30_000;

type ProvidersProps = {
  readonly children: ReactNode;
};

/**
 * Enveloppe l'application dans ses fournisseurs.
 *
 * Le client TanStack Query est créé une seule fois par montage (`useState`), et non au niveau
 * du module : chaque test, ou chaque rendu serveur futur, obtient ainsi un cache isolé.
 */
export function Providers({ children }: ProvidersProps) {
  const [clientRequetes] = useState(
    () => new QueryClient({ defaultOptions: { queries: { staleTime: DUREE_FRAICHEUR_DONNEES } } }),
  );

  return (
    <QueryClientProvider client={clientRequetes}>
      <BrowserRouter>{children}</BrowserRouter>
    </QueryClientProvider>
  );
}
