// Aide de test : affiche un hook de `services` dans un cache de requêtes neuf.
import { renderHook } from '@testing-library/react';

import { creerClientRequetes, creerEnveloppe } from './enveloppeRequetes';

/**
 * Rend `hook` avec son propre cache TanStack Query, réglé comme celui de l'application (un refus de
 * l'API apparaît tout de suite, une panne est rejouée sans attente) : aucun résultat ne fuite d'un
 * test à l'autre. Un test qui doit
 * partager le cache entre plusieurs hooks ou y lire des données utilise `creerEnveloppe` à la place.
 */
export function afficherHook<Resultat>(hook: () => Resultat) {
  return renderHook(hook, { wrapper: creerEnveloppe(creerClientRequetes()) });
}
