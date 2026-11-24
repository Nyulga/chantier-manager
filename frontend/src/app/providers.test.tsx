// Tests des fournisseurs globaux : ils affichent leurs enfants et fournissent TanStack Query.
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { render, screen, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { describe, expect, it, vi } from 'vitest';

import { reponseProbleme } from '@/test/reponseProbleme';
import { SondeLectureChantiers } from '@/test/SondeLectureChantiers';
import { installerServeurApi } from '@/test/serveurApiSimule';

import { Providers } from './providers';

/** Un peu plus que les 30 secondes de fraîcheur prévues : la donnée est alors périmée. */
const DELAI_APRES_FRAICHEUR_MS = 31_000;

/** Composant de test : n'affiche du texte que si un client TanStack Query est disponible. */
function SondeClientRequetes() {
  useQueryClient();
  return <p>Client de requêtes disponible</p>;
}

/** Composant de test : lit une donnée serveur avec la clé et la lecture qu'on lui donne. */
function SondeLecture({ lecture }: { readonly lecture: () => Promise<string> }) {
  const { data } = useQuery({ queryKey: ['sonde'], queryFn: lecture });
  return <p>{data ?? 'Chargement'}</p>;
}

it('fournit le client TanStack Query aux composants enfants', () => {
  render(
    <Providers>
      <SondeClientRequetes />
    </Providers>,
  );

  expect(screen.getByText('Client de requêtes disponible')).toBeVisible();
});

it('ne relit pas une donnée encore fraîche quand un écran la réaffiche (changement de page)', async () => {
  const lecture = vi.fn(() => Promise.resolve('Donnée'));
  const { rerender } = render(
    <Providers>
      <SondeLecture lecture={lecture} />
    </Providers>,
  );
  await screen.findByText('Donnée');

  // L'écran disparaît puis revient : c'est ce que fait une navigation entre deux pages.
  rerender(<Providers>{null}</Providers>);
  rerender(
    <Providers>
      <SondeLecture lecture={lecture} />
    </Providers>,
  );

  expect(await screen.findByText('Donnée')).toBeVisible();
  expect(lecture).toHaveBeenCalledTimes(1);
});

it('relit la donnée une fois la durée de fraîcheur dépassée', async () => {
  // Seule l'horloge est simulée : les minuteries réelles servent encore à la lecture asynchrone.
  vi.useFakeTimers({ toFake: ['Date'] });
  const lecture = vi.fn(() => Promise.resolve('Donnée'));
  const { rerender } = render(
    <Providers>
      <SondeLecture lecture={lecture} />
    </Providers>,
  );
  await screen.findByText('Donnée');

  rerender(<Providers>{null}</Providers>);
  vi.setSystemTime(Date.now() + DELAI_APRES_FRAICHEUR_MS);
  rerender(
    <Providers>
      <SondeLecture lecture={lecture} />
    </Providers>,
  );

  await waitFor(() => {
    expect(lecture).toHaveBeenCalledTimes(2);
  });
  vi.useRealTimers();
});

describe('nouvelle tentative par défaut des requêtes de lecture', () => {
  const serveur = installerServeurApi();

  /**
   * Attente maximale d'une requête qui réussit à la deuxième tentative : TanStack Query laisse
   * une seconde avant de rejouer. L'horloge n'est pas simulée, car les réponses du faux serveur
   * (MSW) passent par de vraies entrées-sorties que des minuteries figées feraient attendre sans fin.
   */
  const ATTENTE_PREMIERE_REPRISE_MS = 3_000;

  /** Réponse de l'API à chaque appel, dans l'ordre ; la dernière se répète. Renvoie le compteur d'appels. */
  function repondreDans(reponses: readonly (() => Response)[]) {
    const compteur = { appels: 0 };
    serveur.use(
      http.get('/api/chantiers', () => {
        const reponse = reponses[Math.min(compteur.appels, reponses.length - 1)];
        compteur.appels += 1;
        return reponse?.();
      }),
    );
    return compteur;
  }

  /** Affiche une requête nue (sans option `retry`) : seul le client de `Providers` décide. */
  function lireAvecProviders() {
    render(
      <Providers>
        <SondeLectureChantiers />
      </Providers>,
    );
  }

  it.each([403, 404])(
    "ne rejoue pas une requête sans option `retry` que l'API refuse (%i)",
    async (statut) => {
      const compteur = repondreDans([() => reponseProbleme(statut, 'Refusé.')]);

      lireAvecProviders();

      // L'état « erreur » n'arrive qu'une fois les reprises épuisées : sans règle, il faudrait 7 s.
      expect(await screen.findByText('error')).toBeVisible();
      expect(compteur.appels).toBe(1);
    },
  );

  it('rejoue une requête sans option `retry` lors d’une panne du serveur (503)', async () => {
    const compteur = repondreDans([
      () => reponseProbleme(503, 'Indisponible.'),
      () => HttpResponse.json([]),
    ]);

    lireAvecProviders();

    expect(
      await screen.findByText('success', {}, { timeout: ATTENTE_PREMIERE_REPRISE_MS }),
    ).toBeVisible();
    expect(compteur.appels).toBe(2);
  });
});
