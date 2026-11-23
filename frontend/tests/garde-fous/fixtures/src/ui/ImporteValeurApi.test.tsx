// Violation volontaire : un test de ui qui importe une valeur de l'API (seuls les types sont permis).
import { client } from '@/api/client';

export const ETAT = client.obtenirEtat();
