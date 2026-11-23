// Aide de test : ce que `GET /api/moi` répond à un chef et à un ouvrier, et le gestionnaire MSW qui choisit selon `X-Profil`.
import { http, HttpResponse } from 'msw';

import type { components } from '@/api/schema';

type Capacites = components['schemas']['CapacitesReponse'];

export const CAPACITES_CHEF: Capacites = {
  role: 'chef',
  peut_creer_chantier: true,
  peut_lister_etapes_a_valider: true,
};

export const CAPACITES_OUVRIER: Capacites = {
  role: 'ouvrier',
  peut_creer_chantier: false,
  peut_lister_etapes_a_valider: false,
};

/**
 * Répond comme l'API : les capacités dépendent du profil envoyé dans l'en-tête `X-Profil`.
 * Les écrans ne devinent rien du profil : un test qui change de profil voit donc les droits suivre.
 */
export const gestionnaireCapacites = http.get('/api/moi', ({ request }) =>
  HttpResponse.json(
    request.headers.get('X-Profil') === 'ouvrier' ? CAPACITES_OUVRIER : CAPACITES_CHEF,
  ),
);
