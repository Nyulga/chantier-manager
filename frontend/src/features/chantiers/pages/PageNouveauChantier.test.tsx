// Tests de la page « nouveau chantier » : droit de création, saisie, envoi, erreurs de l'API par champ et arrivée sur le détail.
import { fireEvent, screen } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { Route, Routes } from 'react-router';
import { afterEach, beforeEach, expect, it } from 'vitest';

import { afficherAvecFournisseurs } from '@/test/afficherAvecFournisseurs';
import { gestionnaireCapacites } from '@/test/capacites';
import { chantierDeTest } from '@/test/chantierDeTest';
import { reponseProbleme } from '@/test/reponseProbleme';
import { installerServeurApi } from '@/test/serveurApiSimule';
import { verifierAccessibilite } from '@/test/verifierAccessibilite';

import { PageNouveauChantier } from './PageNouveauChantier';

const serveur = installerServeurApi();

beforeEach(() => {
  serveur.use(gestionnaireCapacites);
});

afterEach(() => {
  localStorage.clear();
});

const SAISIES = [
  ['Nom du chantier', 'Rénovation de la mairie'],
  ['Voie', '12 rue des Lilas'],
  ['Code postal', '69003'],
  ['Ville', 'Lyon'],
  ['Client', 'Mairie de Lyon'],
  ['Date de début', '2026-03-02'],
  ['Échéance', '2026-09-30'],
  ['Budget (en euros)', '18450.00'],
] as const;

function afficherPage() {
  return afficherAvecFournisseurs(
    <Routes>
      <Route path="/chantiers/nouveau" element={<PageNouveauChantier />} />
      <Route path="/chantiers/:id" element={<p>Détail du chantier</p>} />
    </Routes>,
    '/chantiers/nouveau',
  );
}

async function remplirEtEnvoyer() {
  await screen.findByLabelText('Nom du chantier');
  for (const [libelle, valeur] of SAISIES) {
    fireEvent.change(screen.getByLabelText(libelle), { target: { value: valeur } });
  }
  fireEvent.click(screen.getByRole('button', { name: 'Créer le chantier' }));
}

it('crée le chantier puis ouvre son détail', async () => {
  let corps: unknown = null;
  serveur.use(
    http.post('/api/chantiers', async ({ request }) => {
      corps = await request.json();
      return HttpResponse.json(chantierDeTest(), { status: 201 });
    }),
  );
  afficherPage();

  await remplirEtEnvoyer();

  expect(await screen.findByText('Détail du chantier')).toBeVisible();
  expect(corps).toMatchObject({ nom: 'Rénovation de la mairie', budget: '18450.00' });
});

it("affiche l'erreur globale de l'API, collée au bouton d'envoi, et reste sur le formulaire", async () => {
  serveur.use(
    http.post('/api/chantiers', () =>
      reponseProbleme(422, "L'échéance doit suivre la date de début.", []),
    ),
  );
  afficherPage();

  await remplirEtEnvoyer();

  const alerte = await screen.findByRole('alert');
  const bouton = screen.getByRole('button', { name: 'Créer le chantier' });
  expect(alerte).toHaveTextContent("L'échéance doit suivre la date de début.");
  // Collée au bouton d'envoi : sur mobile, elle est visible au moment où l'on appuie dessus.
  expect(bouton.previousElementSibling).toBe(alerte);
  expect(bouton).toBeEnabled();
});

it('affiche chaque erreur par champ sous son champ, annoncée, sans alerte globale en plus', async () => {
  serveur.use(
    http.post('/api/chantiers', () =>
      reponseProbleme(422, 'Les données envoyées sont invalides.', [
        {
          champ: 'adresse.code_postal',
          message: 'Le code postal ne doit pas dépasser 10 caractères.',
        },
        { champ: 'nom', message: 'Le nom est obligatoire.' },
      ]),
    ),
  );
  afficherPage();

  await remplirEtEnvoyer();

  const codePostal = await screen.findByLabelText('Code postal');
  expect(codePostal).toHaveAccessibleDescription(
    'Le code postal ne doit pas dépasser 10 caractères.',
  );
  expect(codePostal).toBeInvalid();
  expect(screen.getByLabelText('Nom du chantier')).toHaveAccessibleDescription(
    'Le nom est obligatoire.',
  );
  expect(screen.getByLabelText('Ville')).toBeValid();
  // Un message par champ, chacun dans sa propre région annoncée : pas d'alerte « Erreur » en plus.
  expect(screen.getAllByRole('alert')).toHaveLength(2);
  expect(screen.queryByText('Erreur')).not.toBeInTheDocument();
});

it("garde dans l'alerte globale le message d'un champ que le formulaire n'affiche pas", async () => {
  serveur.use(
    http.post('/api/chantiers', () =>
      reponseProbleme(422, 'Les données envoyées sont invalides.', [
        { champ: 'devise', message: 'La devise est inconnue.' },
        { champ: 'client', message: 'Le client est obligatoire.' },
      ]),
    ),
  );
  afficherPage();

  await remplirEtEnvoyer();

  expect(await screen.findByLabelText('Client')).toHaveAccessibleDescription(
    'Le client est obligatoire.',
  );
  expect(screen.getByText('Erreur')).toBeVisible();
  expect(screen.getByText('La devise est inconnue.')).toBeVisible();
});

it("n'affiche pas le formulaire à un ouvrier : une information et un lien de retour à la place", async () => {
  localStorage.setItem('chantier-manager.profil', 'ouvrier');
  afficherPage();

  expect(await screen.findByText('Seul un chef peut créer un chantier.')).toBeVisible();
  expect(screen.queryByLabelText('Nom du chantier')).not.toBeInTheDocument();
  expect(screen.queryByRole('button', { name: 'Créer le chantier' })).not.toBeInTheDocument();
  expect(screen.getByRole('link', { name: 'Retour aux chantiers' })).toHaveAttribute(
    'href',
    '/chantiers',
  );
});

it("n'affiche jamais le formulaire à un ouvrier, pas même pendant le chargement de ses droits", () => {
  localStorage.setItem('chantier-manager.profil', 'ouvrier');
  afficherPage();

  expect(screen.queryByLabelText('Nom du chantier')).not.toBeInTheDocument();
  expect(screen.getByText('Chargement…')).toBeVisible();
});

it("annonce l'erreur de l'API quand les droits ne se chargent pas", async () => {
  serveur.use(http.get('/api/moi', () => reponseProbleme(503, 'Service indisponible.')));
  afficherPage();

  expect(await screen.findByRole('alert')).toHaveTextContent('Service indisponible.');
  expect(screen.queryByLabelText('Nom du chantier')).not.toBeInTheDocument();
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  const { container } = afficherPage();
  await screen.findByLabelText('Nom du chantier');

  await verifierAccessibilite(container);
});

it('affiche le titre de la page et propose de revenir à la liste des chantiers', () => {
  afficherPage();

  expect(screen.getByRole('heading', { level: 1, name: 'Nouveau chantier' })).toBeVisible();
  expect(screen.getByRole('link', { name: 'Retour aux chantiers' })).toHaveAttribute(
    'href',
    '/chantiers',
  );
});
