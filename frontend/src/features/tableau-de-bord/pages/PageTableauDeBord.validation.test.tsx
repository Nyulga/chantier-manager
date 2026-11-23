// Tests de la validation depuis le tableau de bord : erreurs affichées et focus après « Valider ».
import { fireEvent, screen, waitFor, within } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { expect, it } from 'vitest';

import { reponseProbleme } from '@/test/reponseProbleme';
import { ETAPE, ETAPE_SUIVANTE, preparerTableauDeBord } from '@/test/tableauDeBord';

const { serveur, simuler, afficherPage } = preparerTableauDeBord();

it("valide l'étape au clic, avec sa version, et la retire de la liste une fois relue", async () => {
  simuler();
  let corps: unknown = null;
  serveur.use(
    http.post(`/api/etapes/${ETAPE.id}/transitions`, async ({ request }) => {
      corps = await request.json();
      // Après la validation, l'API ne renvoie plus l'étape.
      serveur.use(http.get('/api/etapes/a-valider', () => HttpResponse.json([])));
      return HttpResponse.json({ ...ETAPE, statut: 'validee' });
    }),
  );
  afficherPage();
  const bouton = await screen.findByRole('button', { name: `Valider : ${ETAPE.titre}` });

  fireEvent.click(bouton);

  await waitFor(() => {
    expect(screen.queryByRole('button', { name: /^Valider/ })).not.toBeInTheDocument();
  });
  expect(corps).toEqual({ action: 'valider', version: ETAPE.version });
  expect(screen.getByText(/Rien à valider/)).toBeVisible();
});

it("garde l'erreur 409 de version à l'écran, avec le titre de l'étape, même quand l'étape quitte la liste", async () => {
  simuler();
  serveur.use(
    http.post(`/api/etapes/${ETAPE.id}/transitions`, () => {
      // Un autre chef a déjà validé l'étape : la relecture ne la renvoie plus.
      serveur.use(http.get('/api/etapes/a-valider', () => HttpResponse.json([])));
      return reponseProbleme(409, 'Cette étape a déjà changé de statut.');
    }),
  );
  afficherPage();

  fireEvent.click(await screen.findByRole('button', { name: `Valider : ${ETAPE.titre}` }));

  // La région est relue après l'alerte : le bloc rayé cède la place à la section « Rien à valider ».
  const alerte = await screen.findByRole('alert');
  expect(alerte).toHaveTextContent(
    `Impossible de valider « ${ETAPE.titre} » : Cette étape a déjà changé de statut.`,
  );
  const region = screen.getByRole('region', { name: 'À valider' });
  expect(region).toContainElement(alerte);
  expect(within(region).queryByRole('listitem')).not.toBeInTheDocument();
});

it("affiche l'erreur au niveau de la section, hors des lignes, quand l'étape reste à valider", async () => {
  simuler({ etapes: [ETAPE, ETAPE_SUIVANTE] });
  serveur.use(
    http.post(`/api/etapes/${ETAPE.id}/transitions`, () =>
      reponseProbleme(500, 'Le service est indisponible.'),
    ),
  );
  afficherPage();

  fireEvent.click(await screen.findByRole('button', { name: `Valider : ${ETAPE.titre}` }));

  const alerte = await screen.findByRole('alert');
  expect(alerte).toHaveTextContent(
    `Impossible de valider « ${ETAPE.titre} » : Le service est indisponible.`,
  );
  for (const ligne of screen.getAllByRole('listitem')) {
    expect(ligne).not.toContainElement(alerte);
  }
});

it("remet le focus sur l'étape suivante après une validation réussie", async () => {
  simuler({ etapes: [ETAPE, ETAPE_SUIVANTE] });
  serveur.use(
    http.post(`/api/etapes/${ETAPE.id}/transitions`, () => {
      serveur.use(http.get('/api/etapes/a-valider', () => HttpResponse.json([ETAPE_SUIVANTE])));
      return HttpResponse.json({ ...ETAPE, statut: 'validee' });
    }),
  );
  afficherPage();

  fireEvent.click(await screen.findByRole('button', { name: `Valider : ${ETAPE.titre}` }));

  const region = screen.getByRole('region', { name: 'À valider' });
  await waitFor(() => {
    expect(within(region).getByRole('listitem')).toHaveFocus();
  });
  expect(within(region).getByRole('listitem')).toHaveTextContent(ETAPE_SUIVANTE.titre);
});

it("remet le focus sur le titre de la section quand il n'y a plus d'étape suivante", async () => {
  simuler();
  serveur.use(
    http.post(`/api/etapes/${ETAPE.id}/transitions`, () => {
      serveur.use(http.get('/api/etapes/a-valider', () => HttpResponse.json([])));
      return HttpResponse.json({ ...ETAPE, statut: 'validee' });
    }),
  );
  afficherPage();

  fireEvent.click(await screen.findByRole('button', { name: `Valider : ${ETAPE.titre}` }));

  await waitFor(() => {
    expect(screen.getByRole('heading', { level: 2, name: 'À valider' })).toHaveFocus();
  });
});

it("remet aussi le focus en place après une erreur, sur l'étape suivante", async () => {
  simuler({ etapes: [ETAPE, ETAPE_SUIVANTE] });
  serveur.use(
    http.post(`/api/etapes/${ETAPE.id}/transitions`, () =>
      reponseProbleme(500, 'Le service est indisponible.'),
    ),
  );
  afficherPage();

  fireEvent.click(await screen.findByRole('button', { name: `Valider : ${ETAPE.titre}` }));

  await screen.findByRole('alert');
  const region = screen.getByRole('region', { name: 'À valider' });
  const [, suivante] = within(region).getAllByRole('listitem');
  await waitFor(() => {
    expect(suivante).toHaveFocus();
  });
});
