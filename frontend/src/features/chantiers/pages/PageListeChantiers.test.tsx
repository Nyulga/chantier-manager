// Tests de la page « liste des chantiers » : cartes, liste vide, lien de création et accessibilité.
import { screen, waitFor } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { Route, Routes } from 'react-router';
import { afterEach, beforeEach, expect, it } from 'vitest';

import { afficherAvecFournisseurs } from '@/test/afficherAvecFournisseurs';
import { gestionnaireCapacites } from '@/test/capacites';
import { reponseProbleme } from '@/test/reponseProbleme';
import { installerServeurApi } from '@/test/serveurApiSimule';
import { verifierAccessibilite } from '@/test/verifierAccessibilite';

import { chantierDeTest } from '@/test/chantierDeTest';
import { PageListeChantiers } from './PageListeChantiers';

const serveur = installerServeurApi();

beforeEach(() => {
  serveur.use(gestionnaireCapacites);
});

afterEach(() => {
  localStorage.clear();
});

function afficherPage() {
  return afficherAvecFournisseurs(
    <Routes>
      <Route path="/" element={<PageListeChantiers />} />
    </Routes>,
  );
}

it('affiche une carte par chantier : nom, adresse, avancement, échéance et lien', async () => {
  const chantier = chantierDeTest();
  serveur.use(http.get('/api/chantiers', () => HttpResponse.json([chantier])));

  afficherPage();

  expect(screen.getByRole('heading', { level: 1, name: 'Chantiers' })).toBeVisible();
  expect(await screen.findByRole('heading', { level: 2, name: chantier.nom })).toBeVisible();
  expect(screen.getByText('12 rue des Lilas, 69003 Lyon')).toBeVisible();
  expect(screen.getByText('30/09/2026')).toBeVisible();
  expect(
    screen.getByRole('progressbar', { name: `Avancement de ${chantier.nom}` }),
  ).toHaveAttribute('aria-valuenow', '50');
  expect(screen.getByRole('link', { name: chantier.nom })).toHaveAttribute(
    'href',
    `/chantiers/${chantier.id}`,
  );
});

it('affiche toutes les cartes, sans limite', async () => {
  const chantiers = Array.from({ length: 6 }, (_, i) =>
    chantierDeTest({ id: `chantier-${String(i)}`, nom: `Chantier numéro ${String(i)}` }),
  );
  serveur.use(http.get('/api/chantiers', () => HttpResponse.json(chantiers)));

  afficherPage();

  expect(await screen.findAllByRole('heading', { level: 2, name: /Chantier numéro/ })).toHaveLength(
    6,
  );
});

it("affiche un message quand il n'y a aucun chantier", async () => {
  serveur.use(http.get('/api/chantiers', () => HttpResponse.json([])));

  afficherPage();

  expect(await screen.findByText('Aucun chantier pour le moment.')).toBeVisible();
});

it("propose « Nouveau chantier » quand l'API annonce le droit de créer un chantier", async () => {
  serveur.use(http.get('/api/chantiers', () => HttpResponse.json([])));

  afficherPage();

  expect(await screen.findByRole('link', { name: 'Nouveau chantier' })).toHaveAttribute(
    'href',
    '/chantiers/nouveau',
  );
});

it("ne propose pas « Nouveau chantier » quand l'API ne l'annonce pas", async () => {
  localStorage.setItem('chantier-manager.profil', 'ouvrier');
  serveur.use(http.get('/api/chantiers', () => HttpResponse.json([])));

  afficherPage();

  await screen.findByText('Aucun chantier pour le moment.');
  // Les droits arrivent par une requête à part : on attend qu'elle soit passée.
  await waitFor(() => {
    expect(screen.queryByRole('link', { name: 'Nouveau chantier' })).not.toBeInTheDocument();
  });
  expect(screen.queryByRole('link', { name: 'Nouveau chantier' })).not.toBeInTheDocument();
});

it("affiche le message de l'API quand la liste ne peut pas être chargée", async () => {
  serveur.use(http.get('/api/chantiers', () => reponseProbleme(400, 'Profil inconnu.')));

  afficherPage();

  expect(await screen.findByRole('alert')).toHaveTextContent('Profil inconnu.');
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  serveur.use(http.get('/api/chantiers', () => HttpResponse.json([chantierDeTest()])));

  const { container } = afficherPage();
  await screen.findByRole('heading', { level: 2, name: 'Rénovation de la mairie' });

  await verifierAccessibilite(container);
});
