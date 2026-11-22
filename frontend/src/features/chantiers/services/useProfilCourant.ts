// Hook de lecture du profil courant (chef ou ouvrier), pour les écrans des chantiers.
import { useSyncExternalStore } from 'react';

import { ecouterProfil, lireProfil, type Profil } from '@/api/profil';

/**
 * Renvoie le profil choisi, sans pouvoir le changer (le changement est dans `useProfil`).
 *
 * Une fonctionnalité ne peut pas importer une autre (règle 05) : la liste des chantiers relit donc
 * le profil à la même source que `useProfil`, localStorage. Il ne sert qu'à masquer le lien
 * « Nouveau chantier » à l'ouvrier ; l'API reste seule juge (elle répond 403 à un ouvrier).
 */
export function useProfilCourant(): Profil {
  return useSyncExternalStore(ecouterProfil, lireProfil);
}
