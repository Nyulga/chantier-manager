// Tests de la page « tableau de bord » (adresse `/`) : à valider, chantiers, activité et profils.
import { fireEvent, screen, waitFor, within } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { Route, Routes } from 'react-router';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';

import { afficherAvecFournisseurs } from '@/ui/test/afficherAvecFournisseurs';
import { installerServeurApi } from '@/ui/test/serveurApiSimule';
import { verifierAccessibilite } from '@/ui/test/verifierAccessibilite';

import { activiteDeTest } from '../services/activiteDeTest';
import { chantierDeTest } from '../services/chantierDeTest';
import { etapeAValiderDeTest } from '../services/etapeAValiderDeTest';
import { PageTableauDeBord } from './PageTableauDeBord';

const serveur = installerServeurApi();
const CHANTIER = chantierDeTest({ etapes_a_valider: 1 });
const ETAPE = etapeAValiderDeTest();

beforeEach(() => {
  // Seule la date est figée : les délais de MSW et de `waitFor` gardent leur horloge réelle.
  vi.useFakeTimers({ toFake: ['Date'] });
  vi.setSystemTime(new Date(2026, 10, 22, 10, 0));
});

afterEach(() => {
  vi.useRealTimers();
  localStorage.clear();
});

/** Réponses par défaut : un chantier, une étape à valider signalée hier, une entrée d'activité. */
function simuler(surcharges: { chantiers?: unknown; etapes?: unknown; activite?: unknown } = {}) {
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

it('affiche la date du jour, le titre de la page, la recherche « Bientôt » et la création pour un chef', async () => {
  simuler();

  afficherPage();

  expect(screen.getByText('dimanche 22 novembre 2026')).toBeVisible();
  expect(screen.getByRole('heading', { level: 1, name: 'Tableau de bord' })).toBeVisible();
  expect(screen.getByRole('searchbox', { name: 'Rechercher un chantier' })).toBeDisabled();
  expect(screen.getByText('Bientôt')).toBeVisible();
  expect(screen.getByRole('link', { name: 'Nouveau chantier' })).toHaveAttribute(
    'href',
    '/chantiers/nouveau',
  );
  await screen.findByRole('region', { name: 'À valider' });
});

it('liste les étapes à valider avec leur chantier, leur signalement, « Examiner » et « Valider »', async () => {
  simuler();

  afficherPage();

  await screen.findByText(ETAPE.titre);
  const region = screen.getByRole('region', { name: 'À valider' });
  expect(within(region).getByText('1')).toBeVisible();
  expect(within(region).getByText(ETAPE.titre)).toBeVisible();
  expect(within(region).getByText(CHANTIER.nom)).toBeVisible();
  expect(within(region).getByText('Signalée hier à 17:42')).toBeVisible();
  expect(within(region).getByRole('link', { name: `Examiner : ${ETAPE.titre}` })).toHaveAttribute(
    'href',
    `/chantiers/${ETAPE.chantier_id}`,
  );
  expect(within(region).getByRole('button', { name: `Valider : ${ETAPE.titre}` })).toBeVisible();
});

it('n’affiche pas « Valider » quand l’API ne permet pas cette action', async () => {
  simuler({ etapes: [{ ...ETAPE, actions_permises: [] }] });

  afficherPage();

  await screen.findByText(ETAPE.titre);
  const region = screen.getByRole('region', { name: 'À valider' });
  expect(within(region).queryByRole('button', { name: /^Valider/ })).not.toBeInTheDocument();
});

it('valide l’étape au clic et la retire de la liste une fois relue', async () => {
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
  expect(corps).toEqual({ action: 'valider' });
  expect(screen.getByText(/Rien à valider/)).toBeVisible();
});

it('affiche près de l’action l’erreur 409 de l’API', async () => {
  simuler();
  serveur.use(
    http.post(`/api/etapes/${ETAPE.id}/transitions`, () =>
      HttpResponse.json(
        { status: 409, detail: 'Cette étape a déjà changé de statut.' },
        { status: 409, headers: { 'Content-Type': 'application/problem+json' } },
      ),
    ),
  );
  afficherPage();

  fireEvent.click(await screen.findByRole('button', { name: `Valider : ${ETAPE.titre}` }));

  const region = screen.getByRole('region', { name: 'À valider' });
  expect(await within(region).findByRole('alert')).toHaveTextContent(
    'Cette étape a déjà changé de statut.',
  );
});

it('dit qu’il n’y a rien à valider quand la liste est vide', async () => {
  simuler({ etapes: [] });

  afficherPage();

  expect(await screen.findByText(/Rien à valider/)).toBeVisible();
});

it('affiche l’erreur de l’API quand les étapes à valider ne se chargent pas', async () => {
  simuler();
  serveur.use(
    http.get('/api/etapes/a-valider', () =>
      HttpResponse.json(
        { status: 500, detail: 'Le service est indisponible.' },
        { status: 500, headers: { 'Content-Type': 'application/problem+json' } },
      ),
    ),
  );

  afficherPage();

  const region = await screen.findByRole('region', { name: 'À valider' });
  expect(await within(region).findByRole('alert')).toHaveTextContent(
    'Le service est indisponible.',
  );
});

it('annonce le chargement des étapes à valider', () => {
  simuler();

  afficherPage();

  expect(screen.getByText('Chargement des étapes à valider…')).toBeVisible();
});

it('ne montre ni « À valider » ni « Nouveau chantier » à un ouvrier, et ne demande pas la liste à l’API', async () => {
  localStorage.setItem('chantier-manager.profil', 'ouvrier');
  // Aucune réponse n'est prévue pour `/api/etapes/a-valider` : l'appel ferait échouer le test.
  serveur.use(
    http.get('/api/chantiers', () => HttpResponse.json([CHANTIER])),
    http.get('/api/activite', () => HttpResponse.json([])),
  );

  afficherPage();

  await screen.findByRole('heading', { level: 3, name: CHANTIER.nom });
  expect(screen.queryByRole('region', { name: 'À valider' })).not.toBeInTheDocument();
  expect(screen.queryByRole('link', { name: 'Nouveau chantier' })).not.toBeInTheDocument();
});

it('affiche les cartes de chantiers et un lien vers la liste complète', async () => {
  simuler({ chantiers: [CHANTIER], etapes: [] });

  afficherPage();

  const region = await screen.findByRole('region', { name: 'Mes chantiers' });
  expect(
    await within(region).findByRole('heading', { level: 3, name: CHANTIER.nom }),
  ).toBeVisible();
  expect(within(region).getByRole('link', { name: 'Voir le chantier' })).toHaveAttribute(
    'href',
    '/chantiers',
  );
});

it('affiche l’activité récente avec le chantier et le moment, et « Toi » pour le profil courant', async () => {
  const moment = new Date(2026, 10, 21, 17, 45).toISOString();
  simuler({
    activite: [
      activiteDeTest({
        role: 'chef',
        ancien_statut: 'terminee_a_valider',
        nouveau_statut: 'en_cours',
        commentaire: 'Reprise côté nord',
        date: moment,
      }),
      activiteDeTest({ role: 'ouvrier', date: moment }),
    ],
  });

  afficherPage();

  const liste = await screen.findByRole('list', { name: 'Activité récente' });
  const [refus, signalement] = within(liste).getAllByRole('listitem');
  expect(refus).toHaveTextContent('Toi as refusé « Pose des meubles » : Reprise côté nord');
  expect(refus).toHaveTextContent(`${CHANTIER.nom} · hier à 17:45`);
  expect(signalement).toHaveTextContent('L’ouvrier a signalé « Pose des meubles » terminée');
});

it('n’a aucun défaut d’accessibilité détectable par axe', async () => {
  simuler();
  const { container } = afficherPage();
  await screen.findByRole('list', { name: 'Activité récente' });

  await verifierAccessibilite(container);
});
