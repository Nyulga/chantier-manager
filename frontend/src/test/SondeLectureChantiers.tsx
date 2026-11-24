// Aide de test : un composant qui lit la liste des chantiers SANS poser aucune règle de nouvelle tentative.
import { useQuery } from '@tanstack/react-query';

import { listerChantiers } from '@/api/chantiers';

/**
 * Lit `/api/chantiers` avec une requête nue : ni `retry` ni `retryDelay`. Ce qu'elle fait en cas
 * d'échec ne vient donc que des options par défaut du client de requêtes, ce qui permet de prouver
 * que ce client rejoue les pannes et jamais une réponse définitive de l'API.
 */
export function SondeLectureChantiers() {
  const { status } = useQuery({ queryKey: ['sonde-lecture-chantiers'], queryFn: listerChantiers });
  return <p>{status}</p>;
}
