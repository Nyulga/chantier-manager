// Tests des fournisseurs globaux : ils affichent leurs enfants et fournissent TanStack Query.
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { render, screen, waitFor } from '@testing-library/react';
import { expect, it, vi } from 'vitest';

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
