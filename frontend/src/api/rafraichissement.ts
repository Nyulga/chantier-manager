// Rafraîchissement du cache après une modification des étapes d'un chantier.
import type { QueryClient } from '@tanstack/react-query';

import { clesRequetes } from './clesRequetes';

/**
 * Invalide ce qu'une modification d'étape peut avoir changé dans un chantier : la liste des
 * chantiers et le chantier concerné (leur avancement et leurs compteurs sont calculés par l'API).
 * Les étapes du chantier sont relues avec lui : leur clé commence par celle du chantier,
 * l'invalidation par préfixe les couvre.
 */
export async function rafraichirChantier(
  clientRequetes: QueryClient,
  chantierId: string,
): Promise<void> {
  await Promise.all([
    clientRequetes.invalidateQueries({ queryKey: clesRequetes.listeChantiers() }),
    clientRequetes.invalidateQueries({ queryKey: clesRequetes.chantier(chantierId) }),
  ]);
}

/**
 * Invalide en plus ce qu'une transition de statut change sur le tableau de bord : les étapes à
 * valider et le fil d'activité. Il est partagé par les hooks de plusieurs fonctionnalités, pour
 * qu'une action faite sur la page d'un chantier mette aussi à jour le tableau de bord, et
 * inversement. Un simple ajout d'étape n'en a pas besoin : il n'utilise que `rafraichirChantier`.
 */
export async function rafraichirApresTransition(
  clientRequetes: QueryClient,
  chantierId: string,
): Promise<void> {
  await Promise.all([
    rafraichirChantier(clientRequetes, chantierId),
    clientRequetes.invalidateQueries({ queryKey: clesRequetes.etapesAValider() }),
    clientRequetes.invalidateQueries({ queryKey: clesRequetes.activite() }),
  ]);
}
