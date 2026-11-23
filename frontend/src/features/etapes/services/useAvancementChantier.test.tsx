// Tests du hook `useAvancementChantier` : l'avancement et le droit d'ajouter une étape, lus dans le chantier de l'API.
import { waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { expect, it } from 'vitest';

import { chantierDeTest } from '@/test/chantierDeTest';
import { reponseProbleme } from '@/test/reponseProbleme';
import { afficherHook } from '@/test/afficherHook';
import { installerServeurApi } from '@/test/serveurApiSimule';

import { useAvancementChantier } from './useAvancementChantier';

const serveur = installerServeurApi();

function afficher(id: string) {
  return afficherHook(() => useAvancementChantier(id));
}

it("renvoie l'avancement et le droit d'ajouter une étape, tels que l'API les donne", async () => {
  const chantier = chantierDeTest({ avancement: 40, peut_ajouter_etape: false });
  serveur.use(http.get(`/api/chantiers/${chantier.id}`, () => HttpResponse.json(chantier)));

  const { result } = afficher(chantier.id);

  await waitFor(() => {
    expect(result.current.data).toEqual({ avancement: 40, peutAjouterEtape: false });
  });
});

it("expose le message de l'API quand le chantier n'existe pas", async () => {
  serveur.use(
    http.get('/api/chantiers/inconnu', () => reponseProbleme(404, 'Chantier introuvable.')),
  );

  const { result } = afficher('inconnu');

  await waitFor(() => {
    expect(result.current.error?.message).toBe('Chantier introuvable.');
  });
});
