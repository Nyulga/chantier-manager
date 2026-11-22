// Tests de la page « tableau de bord » (adresse `/`) : à valider, chantiers, activité et profils.
import { screen, waitFor, within } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { expect, it } from 'vitest';

import { verifierAccessibilite } from '@/ui/test/verifierAccessibilite';

import { activiteDeTest } from '../services/activiteDeTest';
import { CHANTIER, erreurProbleme, ETAPE, preparerTableauDeBord } from './tableauDeBordDeTest';

const { serveur, simuler, afficherPage } = preparerTableauDeBord();

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

it('masque « À valider » à un ouvrier quand l’API refuse (403), sans afficher d’erreur', async () => {
  localStorage.setItem('chantier-manager.profil', 'ouvrier');
  let demandes = 0;
  serveur.use(
    http.get('/api/chantiers', () => HttpResponse.json([CHANTIER])),
    http.get('/api/activite', () => HttpResponse.json([])),
    http.get('/api/etapes/a-valider', ({ request }) => {
      // Seules les demandes de l'ouvrier comptent : un test précédent peut laisser une requête en vol.
      if (request.headers.get('X-Profil') === 'ouvrier') {
        demandes += 1;
      }
      return erreurProbleme(403, 'Action réservée à un chef.');
    }),
  );

  afficherPage();

  await screen.findByRole('heading', { level: 3, name: CHANTIER.nom });
  await waitFor(() => {
    expect(screen.queryByRole('region', { name: 'À valider' })).not.toBeInTheDocument();
  });
  expect(demandes).toBe(1);
  expect(screen.queryByRole('alert')).not.toBeInTheDocument();
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

it('affiche l’activité récente avec le chantier et le moment, et « Tu » pour le profil courant', async () => {
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
  expect(refus).toHaveTextContent('Tu as refusé « Pose des meubles » : Reprise côté nord');
  expect(refus).toHaveTextContent(`${CHANTIER.nom} · hier à 17:45`);
  expect(signalement).toHaveTextContent('L’ouvrier a signalé « Pose des meubles » terminée');
});

it('n’a aucun défaut d’accessibilité détectable par axe', async () => {
  simuler();
  const { container } = afficherPage();
  await screen.findByRole('list', { name: 'Activité récente' });

  await verifierAccessibilite(container);
});
