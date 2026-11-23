// Hook du profil courant : lire le profil choisi (chef ou ouvrier) et en changer.
import { useQueryClient } from '@tanstack/react-query';
import { useEffect, useSyncExternalStore } from 'react';

import { ecouterProfil, enregistrerProfil, lireProfil } from '@/api/profil';

/**
 * Renvoie le profil courant et `changerProfil`.
 *
 * Le profil vit dans localStorage (source de vérité, relue par le client API à chaque requête) :
 * `useSyncExternalStore` garde tous les composants synchronisés avec lui, sans contexte à
 * déclarer. Les chantiers, les actions permises et le budget visibles dépendent du profil : à
 * chaque changement, le cache est vidé (`resetQueries`) et non seulement marqué périmé. Avec une
 * simple invalidation, le budget et les boutons du chef resteraient à l'écran pendant que l'API
 * répond pour l'ouvrier.
 *
 * Le cache est aussi vidé quand un autre onglet change de profil : le profil est partagé entre
 * onglets par localStorage, et les requêtes de celui-ci partiraient désormais avec le nouveau.
 */
export function useProfil() {
  const clientRequetes = useQueryClient();
  const profil = useSyncExternalStore(ecouterProfil, lireProfil);

  useEffect(() => {
    let dernierProfil = lireProfil();
    return ecouterProfil(() => {
      const profilActuel = lireProfil();
      // `storage` signale aussi les clés étrangères à l'application : on ne vide que sur un vrai changement.
      if (profilActuel !== dernierProfil) {
        dernierProfil = profilActuel;
        void clientRequetes.resetQueries();
      }
    });
  }, [clientRequetes]);

  return { profil, changerProfil: enregistrerProfil };
}
