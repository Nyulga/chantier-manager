// Contexte partagé par les tests du tableau de bord : API simulée, date figée et affichage de la page.
import { http, HttpResponse } from 'msw';
import { Route, Routes } from 'react-router';
import { afterEach, beforeEach, vi } from 'vitest';

import { afficherAvecFournisseurs } from '@/ui/test/afficherAvecFournisseurs';
import { installerServeurApi } from '@/ui/test/serveurApiSimule';

import { activiteDeTest } from '../services/activiteDeTest';
import { chantierDeTest } from '../services/chantierDeTest';
import { etapeAValiderDeTest } from '../services/etapeAValiderDeTest';
import { PageTableauDeBord } from './PageTableauDeBord';

export const CHANTIER = chantierDeTest({ etapes_a_valider: 1 });
export const ETAPE = etapeAValiderDeTest();
export const ETAPE_SUIVANTE = etapeAValiderDeTest({
  id: '0198f1a0-0000-7000-8000-0000000000e2',
  titre: 'Faïence',
});

/** Réponse d'erreur de l'API au format `problem+json`. */
export function erreurProbleme(status: number, detail: string) {
  return HttpResponse.json(
    { status, detail },
    { status, headers: { 'Content-Type': 'application/problem+json' } },
  );
}

type Surcharges = { chantiers?: unknown; etapes?: unknown; activite?: unknown };

/**
 * À appeler en haut d'un fichier de test : installe le serveur simulé, fige la date au dimanche
 * 22 novembre 2026 à 10 h (seule la date : les délais de MSW et de `waitFor` gardent leur horloge
 * réelle) et renvoie de quoi préparer les réponses puis afficher la page.
 */
export function preparerTableauDeBord() {
  const serveur = installerServeurApi();

  beforeEach(() => {
    vi.useFakeTimers({ toFake: ['Date'] });
    vi.setSystemTime(new Date(2026, 10, 22, 10, 0));
  });

  afterEach(() => {
    vi.useRealTimers();
    localStorage.clear();
  });

  /** Réponses par défaut : un chantier, une étape à valider signalée hier, une entrée d'activité. */
  function simuler(surcharges: Surcharges = {}) {
    const signaleeLe = new Date(2026, 10, 21, 17, 42).toISOString();
    serveur.use(
      http.get('/api/chantiers', () => HttpResponse.json(surcharges.chantiers ?? [CHANTIER])),
      http.get('/api/etapes/a-valider', () =>
        HttpResponse.json(surcharges.etapes ?? [{ ...ETAPE, signalee_le: signaleeLe }]),
      ),
      http.get('/api/activite', () => HttpResponse.json(surcharges.activite ?? [activiteDeTest()])),
    );
  }

  function afficherPage() {
    return afficherAvecFournisseurs(
      <Routes>
        <Route path="/" element={<PageTableauDeBord />} />
      </Routes>,
    );
  }

  return { serveur, simuler, afficherPage };
}
