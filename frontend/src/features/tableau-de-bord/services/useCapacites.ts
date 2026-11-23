// Hook des capacités de l'acteur : ce que l'API l'autorise à faire sur le tableau de bord.
import { useQuery } from '@tanstack/react-query';
import { useSyncExternalStore } from 'react';

import { lireCapacites } from '@/api/capacites';
import { clesRequetes } from '@/api/clesRequetes';
import { ecouterProfil, lireProfil } from '@/api/profil';
import { reessayerRequete } from '@/api/reessai';

/**
 * Lit `GET /api/moi` : le lien « Nouveau chantier » et la section « À valider » en dépendent,
 * jamais du profil choisi. Le profil est dans la clé de cache : au changement, la requête repart
 * de zéro et aucun droit de l'ancien profil ne reste affiché pendant l'attente. Tant que la
 * réponse n'est pas là, `data` est `undefined` et les écrans n'affichent rien de ce qui dépend d'un droit.
 */
export function useCapacites() {
  const profil = useSyncExternalStore(ecouterProfil, lireProfil);

  return useQuery({
    queryKey: clesRequetes.capacites(profil),
    retry: reessayerRequete,
    queryFn: lireCapacites,
  });
}
