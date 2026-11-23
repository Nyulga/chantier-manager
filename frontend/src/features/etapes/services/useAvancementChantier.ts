// Hook de l'avancement d'un chantier et du droit d'y ajouter une étape, pour la page des étapes.
import { useQuery } from '@tanstack/react-query';

import { lireChantier } from '@/api/chantiers';
import { clesRequetes } from '@/api/clesRequetes';
import { reessayerRequete } from '@/api/reessai';

/**
 * Lit le chantier et n'en garde que ce que la page des étapes affiche : son avancement et le droit
 * d'ajouter une étape. Les deux viennent de l'API, rien n'est calculé ici.
 *
 * Il partage la clé de cache de la page du chantier : un seul appel, et l'avancement se met à jour
 * quand une action invalide le chantier (voir `rafraichissement.ts`). La page du chantier n'a donc
 * pas à transmettre ces valeurs à celle des étapes, qui est celle d'une autre fonctionnalité.
 */
export function useAvancementChantier(chantierId: string) {
  return useQuery({
    queryKey: clesRequetes.chantier(chantierId),
    retry: reessayerRequete,
    queryFn: () => lireChantier(chantierId),
    select: (chantier) => ({
      avancement: chantier.avancement,
      peutAjouterEtape: chantier.peut_ajouter_etape,
    }),
  });
}
