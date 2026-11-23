// Tests de la page des étapes : actions permises par l'API, refus commenté, ajout, erreurs par champ et avancement.
import { fireEvent, screen, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { Route, Routes } from 'react-router';
import { expect, it } from 'vitest';

import { afficherAvecFournisseurs } from '@/test/afficherAvecFournisseurs';
import { chantierDeTest } from '@/test/chantierDeTest';
import { etapeDeTest } from '@/test/etapeDeTest';
import { reponseProbleme } from '@/test/reponseProbleme';
import { installerServeurApi } from '@/test/serveurApiSimule';
import { verifierAccessibilite } from '@/test/verifierAccessibilite';

import { PageEtapesChantier } from './PageEtapesChantier';

const serveur = installerServeurApi();
const CHANTIER = '0198f1a0-0000-7000-8000-000000000001';

/** Étape telle que l'API la renvoie : le type vient de la fabrique de test. */
type Etape = ReturnType<typeof etapeDeTest>;

/** Ce que l'API dit du chantier : l'avancement et le droit d'ajouter une étape. */
type ResumeChantier = { peutAjouterEtape: boolean; avancement: number };

function afficherAdresse() {
  return afficherAvecFournisseurs(
    <Routes>
      <Route path="/chantiers/:id" element={<PageEtapesChantier />} />
    </Routes>,
    `/chantiers/${CHANTIER}`,
  );
}

function afficherPage(
  etapes: Etape[],
  resume: ResumeChantier = { peutAjouterEtape: true, avancement: 50 },
) {
  serveur.use(
    http.get(`/api/chantiers/${CHANTIER}`, () =>
      HttpResponse.json(
        chantierDeTest({
          id: CHANTIER,
          avancement: resume.avancement,
          peut_ajouter_etape: resume.peutAjouterEtape,
        }),
      ),
    ),
    http.get(`/api/chantiers/${CHANTIER}/etapes`, () => HttpResponse.json(etapes)),
  );
  return afficherAdresse();
}

it("affiche l'avancement tel que l'API le donne, sans compter les étapes", async () => {
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

it("n'affiche que les boutons des actions permises par l'API", async () => {
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

it("n'affiche aucun bouton d'action quand l'API n'en permet aucune", async () => {
  afficherPage([etapeDeTest({ actions_permises: [] })]);

  await screen.findByText('Fondations');
  expect(
    screen.queryByRole('button', { name: /Démarrer|Valider|Refuser|Signaler/ }),
  ).not.toBeInTheDocument();
});

it("envoie l'action choisie à l'API, avec la version de l'étape affichée", async () => {
  let corps: unknown = null;
  serveur.use(
    http.post('/api/etapes/:id/transitions', async ({ request }) => {
      corps = await request.json();
      return HttpResponse.json(etapeDeTest({ statut: 'en_cours' }));
    }),
  );
  afficherPage([etapeDeTest({ version: 7 })]);

  fireEvent.click(await screen.findByRole('button', { name: 'Démarrer : Fondations' }));

  await waitFor(() => {
    expect(corps).toEqual({ action: 'demarrer', version: 7 });
  });
});

it('demande un commentaire pour refuser, puis envoie le refus avec la version', async () => {
  let corps: unknown = null;
  serveur.use(
    http.post('/api/etapes/:id/transitions', async ({ request }) => {
      corps = await request.json();
      return HttpResponse.json(etapeDeTest({ statut: 'en_cours' }));
    }),
  );
  afficherPage([
    etapeDeTest({ version: 3, statut: 'terminee_a_valider', actions_permises: ['refuser'] }),
  ]);

  fireEvent.click(await screen.findByRole('button', { name: 'Refuser : Fondations' }));
  fireEvent.change(screen.getByLabelText('Motif du refus'), { target: { value: 'Mal fini' } });
  fireEvent.click(screen.getByRole('button', { name: 'Confirmer le refus' }));

  await waitFor(() => {
    expect(corps).toEqual({ action: 'refuser', commentaire: 'Mal fini', version: 3 });
  });
});

it("annonce l'erreur 422 du refus sous le champ du motif, sans alerte en haut de page", async () => {
  serveur.use(
    http.post('/api/etapes/:id/transitions', () =>
      reponseProbleme(422, 'Les données envoyées sont invalides.', [
        { champ: 'commentaire', message: 'Le commentaire du refus est obligatoire.' },
      ]),
    ),
  );
  afficherPage([etapeDeTest({ statut: 'terminee_a_valider', actions_permises: ['refuser'] })]);

  fireEvent.click(await screen.findByRole('button', { name: 'Refuser : Fondations' }));
  fireEvent.click(screen.getByRole('button', { name: 'Confirmer le refus' }));

  // Le message est une région « alert » : un lecteur d'écran l'annonce dès qu'il apparaît.
  const alerte = await screen.findByRole('alert');
  expect(alerte).toHaveTextContent('Le commentaire du refus est obligatoire.');
  expect(screen.getByLabelText('Motif du refus')).toHaveAccessibleDescription(
    'Le commentaire du refus est obligatoire.',
  );
  expect(screen.getAllByRole('alert')).toHaveLength(1);
});

it("garde dans le formulaire du refus l'erreur qui ne vise aucun champ", async () => {
  serveur.use(
    http.post('/api/etapes/:id/transitions', () => reponseProbleme(503, 'Service indisponible.')),
  );
  afficherPage([etapeDeTest({ statut: 'terminee_a_valider', actions_permises: ['refuser'] })]);

  fireEvent.click(await screen.findByRole('button', { name: 'Refuser : Fondations' }));
  fireEvent.change(screen.getByLabelText('Motif du refus'), { target: { value: 'Mal fini' } });
  fireEvent.click(screen.getByRole('button', { name: 'Confirmer le refus' }));

  expect(await screen.findByRole('alert')).toHaveTextContent('Service indisponible.');
  expect(screen.getByLabelText('Motif du refus')).toBeVisible();
});

it("affiche l'erreur de version d'une autre action (409) dans la carte de l'étape concernée", async () => {
  serveur.use(
    http.post('/api/etapes/:id/transitions', () =>
      reponseProbleme(409, 'Cette étape a déjà changé de statut.'),
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

it("permet d'annuler le refus", async () => {
  afficherPage([etapeDeTest({ statut: 'terminee_a_valider', actions_permises: ['refuser'] })]);

  fireEvent.click(await screen.findByRole('button', { name: 'Refuser : Fondations' }));
  fireEvent.click(screen.getByRole('button', { name: 'Annuler' }));

  expect(screen.queryByLabelText('Motif du refus')).not.toBeInTheDocument();
});

it("affiche le formulaire d'ajout seulement si l'API le permet", async () => {
  afficherPage([], { peutAjouterEtape: false, avancement: 0 });

  await screen.findByText('Aucune étape pour le moment.');
  expect(screen.queryByLabelText("Titre de l'étape")).not.toBeInTheDocument();
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

  fireEvent.change(await screen.findByLabelText("Titre de l'étape"), {
    target: { value: 'Fondations' },
  });
  fireEvent.click(screen.getByRole('button', { name: "Ajouter l'étape" }));

  await waitFor(() => {
    expect(corps).toEqual({ titre: 'Fondations' });
  });
  expect(await screen.findByLabelText("Titre de l'étape")).toHaveValue('');
});

it("affiche l'erreur par champ de l'ajout sous le champ du titre, annoncée", async () => {
  serveur.use(
    http.post(`/api/chantiers/${CHANTIER}/etapes`, () =>
      reponseProbleme(422, 'Les données envoyées sont invalides.', [
        { champ: 'titre', message: 'Le titre ne doit pas dépasser 200 caractères.' },
      ]),
    ),
  );
  afficherPage([]);

  fireEvent.change(await screen.findByLabelText("Titre de l'étape"), {
    target: { value: 'Fondations' },
  });
  fireEvent.click(screen.getByRole('button', { name: "Ajouter l'étape" }));

  expect(await screen.findByRole('alert')).toHaveTextContent(
    'Le titre ne doit pas dépasser 200 caractères.',
  );
  expect(screen.getByLabelText("Titre de l'étape")).toHaveAccessibleDescription(
    'Le titre ne doit pas dépasser 200 caractères.',
  );
  expect(screen.getByLabelText("Titre de l'étape")).toHaveValue('Fondations');
});

it("affiche dans une alerte le conflit (409) d'un ajout simultané", async () => {
  serveur.use(
    http.post(`/api/chantiers/${CHANTIER}/etapes`, () =>
      reponseProbleme(409, "Une autre personne vient d'ajouter une étape : réessaie."),
    ),
  );
  afficherPage([]);

  fireEvent.change(await screen.findByLabelText("Titre de l'étape"), {
    target: { value: 'Fondations' },
  });
  fireEvent.click(screen.getByRole('button', { name: "Ajouter l'étape" }));

  expect(await screen.findByRole('alert')).toHaveTextContent(
    "Une autre personne vient d'ajouter une étape : réessaie.",
  );
});

it("annonce le chargement des étapes, puis affiche le message de l'API quand elles échouent", async () => {
  serveur.use(
    http.get(`/api/chantiers/${CHANTIER}`, () =>
      HttpResponse.json(chantierDeTest({ id: CHANTIER })),
    ),
    http.get(`/api/chantiers/${CHANTIER}/etapes`, () =>
      reponseProbleme(503, 'Service indisponible.'),
    ),
  );
  afficherAdresse();

  expect(screen.getByText('Chargement des étapes…')).toBeVisible();
  expect(await screen.findByRole('alert')).toHaveTextContent('Service indisponible.');
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  const { container } = afficherPage([
    etapeDeTest({ statut: 'terminee_a_valider', actions_permises: ['valider', 'refuser'] }),
  ]);
  await screen.findByText('Fondations');

  await verifierAccessibilite(container);
});
