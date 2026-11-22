// Aide de test : vérifie qu'un fragment de page n'a aucun défaut d'accessibilité détecté par axe.
import { expect } from 'vitest';
import { axe } from 'vitest-axe';

/**
 * Analyse `element` avec axe et fait échouer le test s'il reste des violations.
 *
 * On compare la liste des violations à une liste vide (plutôt qu'avec un matcher dédié)
 * pour que le rapport d'échec détaille chaque règle enfreinte et chaque nœud concerné.
 * jsdom ne calcule pas les couleurs : le contraste est vérifié dans le navigateur (e2e).
 */
export async function verifierAccessibilite(element: Element): Promise<void> {
  const resultats = await axe(element);

  expect(resultats.violations).toEqual([]);
}
