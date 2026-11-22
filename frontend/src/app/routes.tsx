// Table des routes de l'application : chaque adresse est associée à la page d'une fonctionnalité.
import { Route, Routes } from 'react-router';

import { PageIntrouvable } from '@/features/accueil/pages/PageIntrouvable';
import { PageDetailChantier } from '@/features/chantiers/pages/PageDetailChantier';
import { PageListeChantiers } from '@/features/chantiers/pages/PageListeChantiers';
import { PageNouveauChantier } from '@/features/chantiers/pages/PageNouveauChantier';
import { PageEtapesChantier } from '@/features/etapes/pages/PageEtapesChantier';
import { LayoutApplication } from '@/features/profil/pages/LayoutApplication';

/**
 * Routes de l'application, toutes sous l'en-tête commun. Les étapes sont une route enfant du
 * détail : leur page s'affiche dans l'`Outlet` de `PageDetailChantier`.
 */
export function RoutesApplication() {
  return (
    <Routes>
      <Route element={<LayoutApplication />}>
        <Route index element={<PageListeChantiers />} />
        <Route path="chantiers/nouveau" element={<PageNouveauChantier />} />
        <Route path="chantiers/:id" element={<PageDetailChantier />}>
          <Route index element={<PageEtapesChantier />} />
        </Route>
        <Route path="*" element={<PageIntrouvable />} />
      </Route>
    </Routes>
  );
}
