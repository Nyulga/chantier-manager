// Tests de la page « tableau de bord » (adresse `/`) : à valider, chantiers, activité et profils.
import { act, screen, waitFor, within } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { expect, it } from 'vitest';

import { activiteDeTest } from '@/test/activiteDeTest';
import { reponseProbleme } from '@/test/reponseProbleme';
import { CHANTIER, ETAPE, preparerTableauDeBord } from '@/test/preparerPageTableauDeBord';
import { verifierAccessibilite } from '@/test/verifierAccessibilite';

const { serveur, simuler, afficherPage } = preparerTableauDeBord();

it('affiche la date du jour, le titre de la page, la recherche « Bientôt » et la création pour un chef', async () => {
  simuler();

  afficherPage();

  expect(screen.getByText('dimanche 22 novembre 2026')).toBeVisible();
  expect(screen.getByRole('heading', { level: 1, name: 'Tableau de bord' })).toBeVisible();
  expect(screen.getByRole('searchbox', { name: 'Rechercher un chantier' })).toBeDisabled();
  expect(screen.getByText('Bientôt')).toBeVisible();
  expect(await screen.findByRole('link', { name: 'Nouveau chantier' })).toHaveAttribute(
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

it("n'affiche pas « Valider » quand l'API ne permet pas cette action", async () => {
  simuler({ etapes: [{ ...ETAPE, actions_permises: [] }] });

  afficherPage();

  await screen.findByText(ETAPE.titre);
  const region = screen.getByRole('region', { name: 'À valider' });
  expect(within(region).queryByRole('button', { name: /^Valider/ })).not.toBeInTheDocument();
});

it("dit qu'il n'y a rien à valider quand la liste est vide", async () => {
  simuler({ etapes: [] });

  afficherPage();

  expect(await screen.findByText(/Rien à valider/)).toBeVisible();
});

it("affiche l'erreur de l'API quand les étapes à valider ne se chargent pas", async () => {
  simuler();
  serveur.use(
    http.get('/api/etapes/a-valider', () => reponseProbleme(500, 'Le service est indisponible.')),
  );

  afficherPage();

  const region = await screen.findByRole('region', { name: 'À valider' });
  expect(await within(region).findByRole('alert')).toHaveTextContent(
    'Le service est indisponible.',
  );
});

it('annonce le chargement des étapes à valider une fois les capacités connues', async () => {
  simuler();

  afficherPage();

  expect(await screen.findByText('Chargement des étapes à valider…')).toBeVisible();
});

it("n'affiche pas du tout « À valider » à un ouvrier, et n'interroge pas l'API à ce sujet", async () => {
  localStorage.setItem('chantier-manager.profil', 'ouvrier');
  simuler({ chantiers: [CHANTIER], activite: [] });
  let demandes = 0;
  serveur.use(
    http.get('/api/etapes/a-valider', () => {
      demandes += 1;
      return reponseProbleme(403, 'Action réservée à un chef.');
    }),
  );

  afficherPage();

  // Aucune étape de la page ne montre la section, pas même pendant son chargement.
  expect(screen.queryByRole('region', { name: 'À valider' })).not.toBeInTheDocument();
  expect(screen.queryByText('Chargement des étapes à valider…')).not.toBeInTheDocument();
  await screen.findByRole('heading', { level: 3, name: CHANTIER.nom });
  expect(screen.queryByRole('region', { name: 'À valider' })).not.toBeInTheDocument();
  expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  expect(screen.queryByRole('link', { name: 'Nouveau chantier' })).not.toBeInTheDocument();
  expect(demandes).toBe(0);
});

it('retire « À valider » et « Nouveau chantier » dès que le profil passe à ouvrier', async () => {
  simuler();
  afficherPage();
  await screen.findByRole('region', { name: 'À valider' });

  act(() => {
    // Le profil est dans localStorage : un autre onglet qui le change le fait savoir par `storage`.
    localStorage.setItem('chantier-manager.profil', 'ouvrier');
    window.dispatchEvent(new StorageEvent('storage', { key: 'chantier-manager.profil' }));
  });

  await waitFor(() => {
    expect(screen.queryByRole('region', { name: 'À valider' })).not.toBeInTheDocument();
  });
  expect(screen.queryByRole('link', { name: 'Nouveau chantier' })).not.toBeInTheDocument();
});

it("affiche « 50+ » quand l'API signale que la liste des étapes à valider est coupée", async () => {
  const etapes = Array.from({ length: 50 }, (_, i) => ({
    ...ETAPE,
    id: `0198f1a0-0000-7000-8000-${String(i).padStart(12, '0')}`,
    titre: `Étape ${String(i)}`,
  }));
  simuler();
  serveur.use(
    http.get('/api/etapes/a-valider', () =>
      HttpResponse.json(etapes, { headers: { 'X-Liste-Tronquee': 'true' } }),
    ),
  );

  afficherPage();

  await screen.findByText('Étape 0');
  const region = screen.getByRole('region', { name: 'À valider' });
  expect(within(region).getByText('50+')).toBeVisible();
});

it('affiche le nombre exact quand la liste des étapes à valider est complète', async () => {
  simuler();

  afficherPage();

  await screen.findByText(ETAPE.titre);
  const region = screen.getByRole('region', { name: 'À valider' });
  expect(within(region).getByText('1')).toBeVisible();
  expect(within(region).queryByText('1+')).not.toBeInTheDocument();
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

it("affiche l'activité récente avec le chantier et le moment, et « Tu » pour le profil courant", async () => {
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
  expect(signalement).toHaveTextContent("L'ouvrier a signalé « Pose des meubles » terminée");
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  simuler();
  const { container } = afficherPage();
  await screen.findByRole('list', { name: 'Activité récente' });

  await verifierAccessibilite(container);
});
