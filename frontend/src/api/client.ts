// Client HTTP de l'application : le seul endroit qui connaît l'adresse de l'API.
// Le client est typé par le schéma OpenAPI généré (`schema.d.ts`, recette `just client`) ;
// seuls les hooks de `services` appellent ce client.
import createClient, { type Client } from 'openapi-fetch';

import type { paths } from './schema';

/** Préfixe de l'API : le frontend et l'API sont servis sur le même domaine (pas de CORS). */
export const BASE_API = '/api';

/**
 * Chemins de l'API sans le préfixe `/api`.
 *
 * Le schéma OpenAPI décrit les routes avec leur préfixe (`/api/health`), alors que le client
 * ajoute déjà `BASE_API` : on retire donc le préfixe des types pour ne pas l'écrire deux fois.
 */
export type CheminsApi = {
  [
    Chemin in keyof paths as Chemin extends `${typeof BASE_API}${infer Reste}` ? Reste : Chemin
  ]: paths[Chemin];
};

/**
 * Crée le client de l'API pour les chemins décrits par `Chemins` (types générés par OpenAPI).
 *
 * Les requêtes partent vers le même domaine que la page, sous `/api`.
 */
export function creerClient<Chemins extends object>(): Client<Chemins> {
  return createClient<Chemins>({ baseUrl: BASE_API });
}

/** Crée le client typé par le schéma OpenAPI de l'application. */
export function creerClientApi(): Client<CheminsApi> {
  return createClient<CheminsApi>({ baseUrl: BASE_API });
}
