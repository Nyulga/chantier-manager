// Tests de la table des routes : chaque adresse mène à la bonne page, sous l'en-tête commun.
import { screen } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { expect, it } from 'vitest';

import { afficherAvecFournisseurs } from '@/test/afficherAvecFournisseurs';
import { gestionnaireCapacites } from '@/test/capacites';
import { chantierDeTest } from '@/test/chantierDeTest';
import { reponseProbleme } from '@/test/reponseProbleme';
import { installerServeurApi } from '@/test/serveurApiSimule';

import { RoutesApplication } from './routes';

const serveur = installerServeurApi();

const CHANTIER = chantierDeTest({ avancement: 0, etapes_validees: 0, etapes_total: 0 });
const ID = CHANTIER.id;

function afficher(adresse: string) {
  afficherAvecFournisseurs(<RoutesApplication />, adresse);
}

it("affiche le tableau de bord à l'adresse racine, avec la barre latérale", async () => {
  serveur.use(
    gestionnaireCapacites,
    http.get('/api/chantiers', () => HttpResponse.json([CHANTIER])),
    http.get('/api/etapes/a-valider', () => HttpResponse.json([])),
    http.get('/api/activite', () => HttpResponse.json([])),
  );

  afficher('/');

  expect(screen.getByRole('navigation', { name: 'Navigation principale' })).toBeVisible();
  expect(screen.getByRole('heading', { level: 1, name: 'Tableau de bord' })).toBeVisible();
  expect(await screen.findByRole('heading', { level: 3, name: CHANTIER.nom })).toBeVisible();
});

it('affiche la liste complète des chantiers à /chantiers', async () => {
  serveur.use(http.get('/api/chantiers', () => HttpResponse.json([CHANTIER])));

  afficher('/chantiers');

  expect(screen.getByRole('heading', { level: 1, name: 'Chantiers' })).toBeVisible();
  expect(await screen.findByRole('heading', { level: 2, name: CHANTIER.nom })).toBeVisible();
});

it('affiche le formulaire de création à /chantiers/nouveau', async () => {
  serveur.use(gestionnaireCapacites);

  afficher('/chantiers/nouveau');

  expect(screen.getByRole('heading', { level: 1, name: 'Nouveau chantier' })).toBeVisible();
  expect(await screen.findByLabelText('Nom du chantier')).toBeVisible();
});

it('affiche le détail du chantier avec ses étapes à /chantiers/:id', async () => {
  serveur.use(
    http.get(`/api/chantiers/${ID}`, () => HttpResponse.json(CHANTIER)),
    http.get(`/api/chantiers/${ID}/etapes`, () => HttpResponse.json([])),
  );

  afficher(`/chantiers/${ID}`);

  expect(await screen.findByRole('heading', { level: 1, name: CHANTIER.nom })).toBeVisible();
  expect(await screen.findByText('Aucune étape pour le moment.')).toBeVisible();
});

it("affiche la page introuvable pour un chantier que l'API ne connaît pas", async () => {
  serveur.use(http.get('/api/chantiers/abc', () => reponseProbleme(404, 'Chantier introuvable.')));

  afficher('/chantiers/abc');

  expect(await screen.findByRole('heading', { level: 1, name: 'Page introuvable' })).toBeVisible();
});

it('affiche la page 404 pour une adresse inconnue', () => {
  afficher('/n-importe-quoi');

  expect(screen.getByRole('heading', { level: 1, name: 'Page introuvable' })).toBeVisible();
});
