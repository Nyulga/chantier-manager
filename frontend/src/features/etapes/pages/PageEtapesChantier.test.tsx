// Tests de la page des étapes : actions permises par l'API, refus commenté, ajout et avancement.
import { fireEvent, screen, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { Outlet, Route, Routes } from 'react-router';
import { expect, it } from 'vitest';

import { afficherAvecFournisseurs } from '@/ui/test/afficherAvecFournisseurs';
import { installerServeurApi } from '@/ui/test/serveurApiSimule';
import { verifierAccessibilite } from '@/ui/test/verifierAccessibilite';

import { etapeDeTest } from '../services/etapeDeTest';
import type { Etape } from '../services/useEtapes';
import { PageEtapesChantier } from './PageEtapesChantier';

const serveur = installerServeurApi();
const CHANTIER = '0198f1a0-0000-7000-8000-000000000001';
const PROBLEME = { headers: { 'Content-Type': 'application/problem+json' } };

function afficherPage(etapes: Etape[], contexte = { peutAjouterEtape: true, avancement: 50 }) {
  serveur.use(http.get(`/api/chantiers/${CHANTIER}/etapes`, () => HttpResponse.json(etapes)));
  return afficherAvecFournisseurs(
    <Routes>
      <Route element={<Outlet context={{ chantierId: CHANTIER, ...contexte }} />}>
        <Route path="/chantiers/:id" element={<PageEtapesChantier />} />
      </Route>
    </Routes>,
    `/chantiers/${CHANTIER}`,
  );
}

it('affiche l’avancement tel que l’API le donne, sans compter les étapes', async () => {
  afficherPage([
    etapeDeTest({ id: 'e1', statut: 'validee', actions_permises: [] }),
    etapeDeTest({ id: 'e2', titre: 'Gros œuvre', actions_permises: [] }),
  ]);

  expect(await screen.findByText('50 %')).toBeVisible();
});

it('affiche chaque étape avec son statut en toutes lettres', async () => {
  afficherPage([
    etapeDeTest({ id: 'e1', titre: 'Fondations', statut: 'validee', actions_permises: [] }),
    etapeDeTest({
      id: 'e2',
      titre: 'Gros œuvre',
      statut: 'terminee_a_valider',
      actions_permises: [],
    }),
  ]);

  expect(await screen.findByText('Fondations')).toBeVisible();
  expect(screen.getByText('Validée')).toBeVisible();
  expect(screen.getByText('Terminée (à valider)')).toBeVisible();
});

it('n’affiche que les boutons des actions permises par l’API', async () => {
  afficherPage([
    etapeDeTest({
      statut: 'terminee_a_valider',
      actions_permises: ['signaler_terminee', 'valider', 'refuser'],
    }),
  ]);

  expect(
    await screen.findByRole('button', { name: 'Signaler terminée : Fondations' }),
  ).toBeVisible();
  expect(screen.getByRole('button', { name: 'Valider : Fondations' })).toBeVisible();
  expect(screen.getByRole('button', { name: 'Refuser : Fondations' })).toBeVisible();
  expect(screen.queryByRole('button', { name: /^Démarrer/ })).not.toBeInTheDocument();
});

it('n’affiche aucun bouton d’action quand l’API n’en permet aucune', async () => {
  afficherPage([etapeDeTest({ actions_permises: [] })]);

  await screen.findByText('Fondations');
  expect(
    screen.queryByRole('button', { name: /Démarrer|Valider|Refuser|Signaler/ }),
  ).not.toBeInTheDocument();
});

it('envoie l’action choisie à l’API', async () => {
  let corps: unknown = null;
  serveur.use(
    http.post('/api/etapes/:id/transitions', async ({ request }) => {
      corps = await request.json();
      return HttpResponse.json(etapeDeTest({ statut: 'en_cours' }));
    }),
  );
  afficherPage([etapeDeTest()]);

  fireEvent.click(await screen.findByRole('button', { name: 'Démarrer : Fondations' }));

  await waitFor(() => {
    expect(corps).toEqual({ action: 'demarrer' });
  });
});

it('demande un commentaire pour refuser, puis envoie le refus', async () => {
  let corps: unknown = null;
  serveur.use(
    http.post('/api/etapes/:id/transitions', async ({ request }) => {
      corps = await request.json();
      return HttpResponse.json(etapeDeTest({ statut: 'en_cours' }));
    }),
  );
  afficherPage([etapeDeTest({ statut: 'terminee_a_valider', actions_permises: ['refuser'] })]);

  fireEvent.click(await screen.findByRole('button', { name: 'Refuser : Fondations' }));
  fireEvent.change(screen.getByLabelText('Motif du refus'), { target: { value: 'Mal fini' } });
  fireEvent.click(screen.getByRole('button', { name: 'Confirmer le refus' }));

  await waitFor(() => {
    expect(corps).toEqual({ action: 'refuser', commentaire: 'Mal fini' });
  });
});

it('affiche l’erreur 422 de l’API quand le commentaire du refus manque', async () => {
  serveur.use(
    http.post('/api/etapes/:id/transitions', () =>
      HttpResponse.json(
        { status: 422, detail: 'Le commentaire du refus est obligatoire.' },
        { status: 422, ...PROBLEME },
      ),
    ),
  );
  afficherPage([etapeDeTest({ statut: 'terminee_a_valider', actions_permises: ['refuser'] })]);

  fireEvent.click(await screen.findByRole('button', { name: 'Refuser : Fondations' }));
  fireEvent.click(screen.getByRole('button', { name: 'Confirmer le refus' }));

  // L'erreur est sous le champ du motif (visible sur mobile), pas dans une alerte en haut de page.
  await waitFor(() => {
    expect(screen.getByLabelText('Motif du refus')).toHaveAccessibleDescription(
      'Le commentaire du refus est obligatoire.',
    );
  });
  expect(screen.queryByRole('alert')).not.toBeInTheDocument();
});

it('affiche l’erreur d’une autre action (409) dans la carte de l’étape concernée', async () => {
  serveur.use(
    http.post('/api/etapes/:id/transitions', () =>
      HttpResponse.json(
        { status: 409, detail: 'Cette étape a déjà changé de statut.' },
        { status: 409, ...PROBLEME },
      ),
    ),
  );
  afficherPage([
    etapeDeTest({ id: 'e1', titre: 'Fondations' }),
    etapeDeTest({ id: 'e2', titre: 'Gros œuvre', actions_permises: [] }),
  ]);

  fireEvent.click(await screen.findByRole('button', { name: 'Démarrer : Fondations' }));

  const alerte = await screen.findByRole('alert');
  expect(alerte).toHaveTextContent('Cette étape a déjà changé de statut.');
  expect(screen.getAllByRole('alert')).toHaveLength(1);
  expect(alerte.parentElement).toHaveTextContent('Fondations');
});

it('permet d’annuler le refus', async () => {
  afficherPage([etapeDeTest({ statut: 'terminee_a_valider', actions_permises: ['refuser'] })]);

  fireEvent.click(await screen.findByRole('button', { name: 'Refuser : Fondations' }));
  fireEvent.click(screen.getByRole('button', { name: 'Annuler' }));

  expect(screen.queryByLabelText('Motif du refus')).not.toBeInTheDocument();
});

it('affiche le formulaire d’ajout seulement si l’API le permet', async () => {
  afficherPage([], { peutAjouterEtape: false, avancement: 0 });

  await screen.findByText('Aucune étape pour le moment.');
  expect(screen.queryByLabelText('Titre de l’étape')).not.toBeInTheDocument();
});

it('ajoute une étape et vide le champ', async () => {
  let corps: unknown = null;
  serveur.use(
    http.post(`/api/chantiers/${CHANTIER}/etapes`, async ({ request }) => {
      corps = await request.json();
      return HttpResponse.json(etapeDeTest(), { status: 201 });
    }),
  );
  afficherPage([]);

  fireEvent.change(await screen.findByLabelText('Titre de l’étape'), {
    target: { value: 'Fondations' },
  });
  fireEvent.click(screen.getByRole('button', { name: 'Ajouter l’étape' }));

  await waitFor(() => {
    expect(corps).toEqual({ titre: 'Fondations' });
  });
  expect(await screen.findByLabelText('Titre de l’étape')).toHaveValue('');
});

it('affiche le message de l’API quand les étapes ne se chargent pas', async () => {
  serveur.use(
    http.get(`/api/chantiers/${CHANTIER}/etapes`, () =>
      HttpResponse.json(
        { status: 404, detail: 'Chantier introuvable.' },
        { status: 404, ...PROBLEME },
      ),
    ),
  );
  afficherAvecFournisseurs(
    <Routes>
      <Route
        element={
          <Outlet context={{ chantierId: CHANTIER, peutAjouterEtape: false, avancement: 0 }} />
        }
      >
        <Route path="/chantiers/:id" element={<PageEtapesChantier />} />
      </Route>
    </Routes>,
    `/chantiers/${CHANTIER}`,
  );

  expect(await screen.findByRole('alert')).toHaveTextContent('Chantier introuvable.');
});

it('n’a aucun défaut d’accessibilité détectable par axe', async () => {
  const { container } = afficherPage([
    etapeDeTest({ statut: 'terminee_a_valider', actions_permises: ['valider', 'refuser'] }),
  ]);
  await screen.findByText('Fondations');

  await verifierAccessibilite(container);
});
