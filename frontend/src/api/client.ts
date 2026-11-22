// Client HTTP de l'application : le seul endroit qui connaît l'adresse de l'API.
// Le client typé, généré depuis le schéma OpenAPI, remplacera le type vide de `creerClient`
// à l'étape suivante du lot ; seuls les hooks de `services` appellent ce client.
import createClient, { type Client } from 'openapi-fetch';

/** Préfixe de l'API : le frontend et l'API sont servis sur le même domaine (pas de CORS). */
export const BASE_API = '/api';

/**
 * Crée le client de l'API pour les chemins décrits par `Chemins` (types générés par OpenAPI).
 *
 * Les requêtes partent vers le même domaine que la page, sous `/api`.
 */
export function creerClient<Chemins extends object>(): Client<Chemins> {
  return createClient<Chemins>({ baseUrl: BASE_API });
}
