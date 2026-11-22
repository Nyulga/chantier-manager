// Client HTTP de l'application : le seul endroit qui connaît l'adresse de l'API.
// Le client est typé par le schéma OpenAPI généré (`schema.d.ts`, recette `just client`) ;
// seuls les hooks de `services` appellent ce client.
import createClient, { type Client, type Middleware } from 'openapi-fetch';

import { lireProfil } from './profil';
import type { paths } from './schema';

/** Préfixe de l'API : le frontend et l'API sont servis sur le même domaine (pas de CORS). */
export const BASE_API = '/api';

/** Nom de l'en-tête qui indique à l'API le profil choisi (squelette sans authentification). */
export const EN_TETE_PROFIL = 'X-Profil';

/**
 * Ajoute le profil courant à chaque requête.
 *
 * Le profil est relu à chaque envoi (et non à la création du client) : un changement de profil
 * est ainsi pris en compte tout de suite, sans devoir recréer les clients déjà utilisés.
 */
const envoyerProfil: Middleware = {
  onRequest({ request }) {
    request.headers.set(EN_TETE_PROFIL, lireProfil());
    return request;
  },
};

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
 * Les requêtes partent vers le même domaine que la page, sous `/api`, avec l'en-tête `X-Profil`.
 */
export function creerClient<Chemins extends object>(): Client<Chemins> {
  const client = createClient<Chemins>({ baseUrl: BASE_API });
  client.use(envoyerProfil);
  return client;
}

/** Crée le client typé par le schéma OpenAPI de l'application. */
export function creerClientApi(): Client<CheminsApi> {
  return creerClient<CheminsApi>();
}
