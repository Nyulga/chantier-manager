// Aide de test : un faux serveur d'API (MSW) branché sur le cycle de vie de Vitest.
import { setupServer } from 'msw/node';
import { afterAll, afterEach, beforeAll } from 'vitest';

/**
 * Crée le serveur simulé et le démarre pour tout le fichier de test.
 *
 * Toute requête sans réponse prévue fait échouer le test (`onUnhandledFrame: 'error'`) : on
 * découvre tout de suite un appel réseau oublié plutôt que de le laisser partir pour de vrai.
 * Les réponses ajoutées avec `serveur.use` sont retirées après chaque test.
 */
export function installerServeurApi() {
  const serveur = setupServer();

  beforeAll(() => {
    serveur.listen({ onUnhandledFrame: 'error' });
  });
  afterEach(() => {
    serveur.resetHandlers();
  });
  afterAll(() => {
    serveur.close();
  });

  return serveur;
}
