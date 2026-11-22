// En-tête commun à toutes les pages : titre de l'application et choix du profil.
import { Outlet } from 'react-router';

import { Page, SelecteurProfil, Titre } from '@/ui';

import { useProfil } from '../services/useProfil';

/**
 * Cadre de chaque écran : le titre « Chantier Manager » (seul titre de niveau 1), le sélecteur
 * de profil relié à `useProfil`, puis la page de la route courante (`Outlet`). Il porte le seul
 * élément `main` de l'écran ; les pages n'en ajoutent pas.
 */
export function LayoutApplication() {
  const { profil, changerProfil } = useProfil();

  return (
    <Page>
      <Titre niveau={1}>Chantier Manager</Titre>
      <SelecteurProfil valeur={profil} onChange={changerProfil} />
      <Outlet />
    </Page>
  );
}
