// Table des routes de l'application : chaque adresse est associée à la page d'une fonctionnalité.
import { Route, Routes } from 'react-router';

import { PageAccueil } from '@/features/accueil/pages/PageAccueil';

/** Routes de l'application. Les nouvelles pages s'ajoutent ici, une ligne par adresse. */
export function RoutesApplication() {
  return (
    <Routes>
      <Route path="/" element={<PageAccueil />} />
    </Routes>
  );
}
