// Hook du droit de créer un chantier : ce que l'API annonce pour l'acteur, jamais ce que le profil laisse deviner.
import { useQuery } from '@tanstack/react-query';
import { useSyncExternalStore } from 'react';

import { lireCapacites } from '@/api/capacites';
import { clesRequetes } from '@/api/clesRequetes';
import { ecouterProfil, lireProfil } from '@/api/profil';
import { reessayerRequete } from '@/api/reessai';

/**
 * Lit `GET /api/moi` et n'en garde que `peut_creer_chantier` : le lien « Nouveau chantier » et la
 * page de création en dépendent. Le profil est dans la clé de cache : au changement, la requête
 * repart de zéro et le droit de l'ancien profil ne reste pas affiché pendant l'attente. Tant que
 * la réponse n'est pas là, `data` est `undefined` et les écrans n'affichent rien qui en dépende.
 */
export function usePeutCreerChantier() {
  const profil = useSyncExternalStore(ecouterProfil, lireProfil);

  return useQuery({
    queryKey: clesRequetes.capacites(profil),
    retry: reessayerRequete,
    queryFn: lireCapacites,
    select: (capacites) => capacites.peut_creer_chantier,
  });
}
