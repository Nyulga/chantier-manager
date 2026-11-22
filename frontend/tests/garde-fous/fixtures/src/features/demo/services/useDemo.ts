// Fixture conforme : un service qui appelle l'API, comme le prévoit la règle 05.
import { client } from '@/api/client';

export function useDemo(): string {
  return client.obtenirEtat();
}
