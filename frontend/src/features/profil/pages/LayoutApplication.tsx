// Cadre commun à toutes les pages : barre latérale (logo, navigation, profil) et zone principale.
import { Outlet } from 'react-router';

import { BarreLaterale, CadreApplication, SelecteurProfil } from '@/ui';

import { NavigationPrincipale } from '../components/NavigationPrincipale';
import { useNombreChantiers } from '../services/useNombreChantiers';
import { useProfil } from '../services/useProfil';

/**
 * Cadre de chaque écran : la barre latérale puis la page de la route courante (`Outlet`), dans le
 * seul élément `main` de l'écran. Chaque page apporte son titre de niveau 1. Le choix du profil
 * est au bas de la barre, à la place de l'utilisateur connecté : le squelette n'a pas de comptes.
 */
export function LayoutApplication() {
  const { profil, changerProfil } = useProfil();
  const nombreChantiers = useNombreChantiers();

  return (
    <CadreApplication
      barreLaterale={
        <BarreLaterale
          navigation={<NavigationPrincipale nombreChantiers={nombreChantiers} />}
          pied={<SelecteurProfil valeur={profil} onChange={changerProfil} />}
        />
      }
    >
      <Outlet />
    </CadreApplication>
  );
}
