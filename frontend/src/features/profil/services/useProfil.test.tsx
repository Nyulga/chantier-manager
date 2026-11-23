// Tests du hook `useProfil` : lecture, changement du profil, et abandon des données de l'ancien profil.
import { useQuery } from '@tanstack/react-query';
import { act, waitFor } from '@testing-library/react';
import { delay, http, HttpResponse } from 'msw';
import { afterEach, expect, it } from 'vitest';

import { listerChantiers } from '@/api/chantiers';
import { clesRequetes } from '@/api/clesRequetes';
import { CLE_PROFIL } from '@/api/profil';
import { chantierDeTest } from '@/test/chantierDeTest';
import { afficherHook } from '@/test/afficherHook';
import { installerServeurApi } from '@/test/serveurApiSimule';

import { useProfil } from './useProfil';

const serveur = installerServeurApi();

afterEach(() => {
  localStorage.clear();
});

function afficher() {
  return afficherHook(() => useProfil());
}

it('renvoie « chef » par défaut', () => {
  const { result } = afficher();

  expect(result.current.profil).toBe('chef');
});

it('lit le profil déjà enregistré', () => {
  localStorage.setItem(CLE_PROFIL, 'ouvrier');

  const { result } = afficher();

  expect(result.current.profil).toBe('ouvrier');
});

it('change le profil, le sauvegarde et met à jour les composants', () => {
  const { result } = afficher();

  act(() => {
    result.current.changerProfil('ouvrier');
  });

  expect(result.current.profil).toBe('ouvrier');
  expect(localStorage.getItem(CLE_PROFIL)).toBe('ouvrier');
});

/**
 * Sonde : la liste des chantiers, dont le budget dépend du profil, lue avec le profil courant.
 * La réponse du chef est immédiate ; celle de l'ouvrier ne vient jamais, pour qu'on puisse
 * regarder ce qui reste à l'écran pendant l'attente.
 */
function useSonde() {
  const chantiers = useQuery({ queryKey: clesRequetes.listeChantiers(), queryFn: listerChantiers });
  return { chantiers, profil: useProfil() };
}

function simulerChantiers() {
  serveur.use(
    http.get('/api/chantiers', async ({ request }) => {
      if (request.headers.get('X-Profil') === 'ouvrier') {
        await delay('infinite');
      }
      return HttpResponse.json([chantierDeTest()]);
    }),
  );
}

async function afficherSondeDuChef() {
  simulerChantiers();
  const rendu = afficherHook(() => useSonde());
  await waitFor(() => {
    expect(rendu.result.current.chantiers.data?.[0]?.budget).toBe('18450.00');
  });
  return rendu;
}

it("ne garde aucune donnée de l'ancien profil pendant le chargement des nouvelles", async () => {
  const { result } = await afficherSondeDuChef();

  act(() => {
    result.current.profil.changerProfil('ouvrier');
  });

  await waitFor(() => {
    expect(result.current.chantiers.data).toBeUndefined();
  });
});

it("abandonne aussi les données de l'ancien profil quand un autre onglet change de profil", async () => {
  const { result } = await afficherSondeDuChef();

  act(() => {
    localStorage.setItem(CLE_PROFIL, 'ouvrier');
    window.dispatchEvent(new StorageEvent('storage', { key: CLE_PROFIL, newValue: 'ouvrier' }));
  });

  await waitFor(() => {
    expect(result.current.chantiers.data).toBeUndefined();
  });
  expect(result.current.profil.profil).toBe('ouvrier');
});

it('garde les données quand le stockage change pour une autre raison que le profil', async () => {
  const { result } = await afficherSondeDuChef();

  act(() => {
    window.dispatchEvent(new StorageEvent('storage', { key: 'autre-cle', newValue: 'x' }));
  });

  expect(result.current.chantiers.data?.[0]?.budget).toBe('18450.00');
});
