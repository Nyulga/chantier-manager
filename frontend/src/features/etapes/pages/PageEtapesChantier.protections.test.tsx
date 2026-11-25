// Tests de la page des étapes face aux protections de la démo : champ piège de l'ajout, plafond, débit, taille et blocage.
import { fireEvent, screen, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { Route, Routes } from 'react-router';
import { expect, it } from 'vitest';

import { afficherAvecFournisseurs } from '@/test/afficherAvecFournisseurs';
import { chantierDeTest } from '@/test/chantierDeTest';
import { etapeDeTest } from '@/test/etapeDeTest';
import { reponseProbleme } from '@/test/reponseProbleme';
import { installerServeurApi } from '@/test/serveurApiSimule';

import { PageEtapesChantier } from './PageEtapesChantier';

const serveur = installerServeurApi();
const CHANTIER = '0198f1a0-0000-7000-8000-000000000001';

/** Affiche la page d'un chantier sans étape, où l'API permet d'en ajouter. */
function afficherPage() {
  serveur.use(
    http.get(`/api/chantiers/${CHANTIER}`, () =>
      HttpResponse.json(chantierDeTest({ id: CHANTIER, peut_ajouter_etape: true })),
    ),
    http.get(`/api/chantiers/${CHANTIER}/etapes`, () => HttpResponse.json([])),
  );
  return afficherAvecFournisseurs(
    <Routes>
      <Route path="/chantiers/:id" element={<PageEtapesChantier />} />
    </Routes>,
    `/chantiers/${CHANTIER}`,
  );
}

it("n'envoie pas le champ piège quand un humain ajoute une étape, et ne le montre pas", async () => {
  let corps: unknown = null;
  serveur.use(
    http.post(`/api/chantiers/${CHANTIER}/etapes`, async ({ request }) => {
      corps = await request.json();
      return HttpResponse.json(etapeDeTest(), { status: 201 });
    }),
  );
  afficherPage();

  fireEvent.change(await screen.findByLabelText("Titre de l'étape"), {
    target: { value: 'Fondations' },
  });
  expect(screen.getAllByRole('textbox')).toHaveLength(1);
  fireEvent.click(screen.getByRole('button', { name: "Ajouter l'étape" }));

  await waitFor(() => {
    expect(corps).toEqual({ titre: 'Fondations' });
  });
});

it("envoie le champ piège de l'ajout quand un robot l'a rempli", async () => {
  let corps: unknown = null;
  serveur.use(
    http.post(`/api/chantiers/${CHANTIER}/etapes`, async ({ request }) => {
      corps = await request.json();
      return reponseProbleme(403, "Cette action n'est pas permise.");
    }),
  );
  const { container } = afficherPage();
  fireEvent.change(await screen.findByLabelText("Titre de l'étape"), {
    target: { value: 'Fondations' },
  });
  const piege = container.querySelector('input[name="site_web"]');
  if (piege === null) {
    throw new Error('Le champ piège est absent du formulaire.');
  }
  fireEvent.change(piege, { target: { value: 'http://exemple.invalid' } });
  fireEvent.click(screen.getByRole('button', { name: "Ajouter l'étape" }));

  expect(await screen.findByRole('alert')).toHaveTextContent("Cette action n'est pas permise.");
  expect(corps).toEqual({ titre: 'Fondations', site_web: 'http://exemple.invalid' });
});

it.each([
  [409, 'Ce chantier a atteint sa limite de 30 étapes.'],
  [429, 'Trop de demandes. Réessaie dans quelques instants.'],
  [413, 'Ta demande est trop volumineuse.'],
  [403, "Cette action n'est pas permise."],
])("affiche dans l'alerte le message d'un refus %i de l'ajout", async (statut, message) => {
  serveur.use(
    http.post(`/api/chantiers/${CHANTIER}/etapes`, () => reponseProbleme(statut, message)),
  );
  afficherPage();

  fireEvent.change(await screen.findByLabelText("Titre de l'étape"), {
    target: { value: 'Fondations' },
  });
  fireEvent.click(screen.getByRole('button', { name: "Ajouter l'étape" }));

  expect(await screen.findByRole('alert')).toHaveTextContent(message);
});
