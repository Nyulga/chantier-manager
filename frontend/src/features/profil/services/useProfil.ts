// Hook du profil courant : lire le profil choisi (chef ou ouvrier) et en changer.
import { useQueryClient } from '@tanstack/react-query';
import { useSyncExternalStore } from 'react';

import { ecouterProfil, enregistrerProfil, lireProfil, type Profil } from '@/api/profil';

/**
 * Renvoie le profil courant et `changerProfil`.
 *
 * Le profil vit dans localStorage (source de vérité, relue par le client API à chaque requête) :
 * `useSyncExternalStore` garde tous les composants synchronisés avec lui, sans contexte à
 * déclarer. Changer de profil invalide le cache TanStack Query, car les chantiers, les actions
 * permises et le budget visibles dépendent du profil : il faut les redemander à l'API.
 */
export function useProfil() {
  const clientRequetes = useQueryClient();
  const profil = useSyncExternalStore(ecouterProfil, lireProfil);

  function changerProfil(nouveau: Profil): void {
    enregistrerProfil(nouveau);
    void clientRequetes.invalidateQueries();
  }

  return { profil, changerProfil };
}
