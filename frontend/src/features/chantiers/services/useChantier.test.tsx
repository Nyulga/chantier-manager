// Tests du hook `useChantier` : un chantier par son identifiant, et l'erreur 404 de l'API.
import { renderHook, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { expect, it } from 'vitest';

import { creerClientRequetes, creerEnveloppe } from '@/api/test/enveloppeRequetes';
import { installerServeurApi } from '@/api/test/serveurApiSimule';

import { chantierDeTest } from './chantierDeTest';
import { useChantier } from './useChantier';

const serveur = installerServeurApi();

it('renvoie le chantier demandé', async () => {
  const chantier = chantierDeTest();
  serveur.use(http.get(`/api/chantiers/${chantier.id}`, () => HttpResponse.json(chantier)));

  const { result } = renderHook(() => useChantier(chantier.id), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });

  await waitFor(() => {
    expect(result.current.data).toEqual(chantier);
  });
});

it('expose le message de l’API quand le chantier n’existe pas', async () => {
  serveur.use(
    http.get('/api/chantiers/inconnu', () =>
      HttpResponse.json(
        { status: 404, detail: 'Chantier introuvable.' },
        { status: 404, headers: { 'Content-Type': 'application/problem+json' } },
      ),
    ),
  );

  const { result } = renderHook(() => useChantier('inconnu'), {
    wrapper: creerEnveloppe(creerClientRequetes()),
  });

  await waitFor(() => {
    expect(result.current.error?.message).toBe('Chantier introuvable.');
  });
});
