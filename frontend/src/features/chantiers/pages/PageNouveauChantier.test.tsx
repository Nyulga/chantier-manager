// Tests de la page « nouveau chantier » : saisie, envoi, erreurs de l'API et arrivée sur le détail.
import { fireEvent, screen } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { Route, Routes } from 'react-router';
import { expect, it } from 'vitest';

import { afficherAvecFournisseurs } from '@/ui/test/afficherAvecFournisseurs';
import { installerServeurApi } from '@/ui/test/serveurApiSimule';
import { verifierAccessibilite } from '@/ui/test/verifierAccessibilite';

import { chantierDeTest } from '../services/chantierDeTest';
import { PageNouveauChantier } from './PageNouveauChantier';

const serveur = installerServeurApi();

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

function remplirEtEnvoyer() {
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

  remplirEtEnvoyer();

  expect(await screen.findByText('Détail du chantier')).toBeVisible();
  expect(corps).toMatchObject({ nom: 'Rénovation de la mairie', budget: '18450.00' });
});

it('affiche l’erreur de l’API et reste sur le formulaire', async () => {
  serveur.use(
    http.post('/api/chantiers', () =>
      HttpResponse.json(
        { status: 422, detail: 'Les données envoyées sont invalides.' },
        { status: 422, headers: { 'Content-Type': 'application/problem+json' } },
      ),
    ),
  );
  afficherPage();

  remplirEtEnvoyer();

  const alerte = await screen.findByRole('alert');
  const bouton = screen.getByRole('button', { name: 'Créer le chantier' });
  expect(alerte).toHaveTextContent('Les données envoyées sont invalides.');
  // Collée au bouton d'envoi : sur mobile, elle est visible au moment où l'on appuie dessus.
  expect(bouton.previousElementSibling).toBe(alerte);
  expect(bouton).toBeEnabled();
});

it('n’a aucun défaut d’accessibilité détectable par axe', async () => {
  const { container } = afficherPage();

  await verifierAccessibilite(container);
});
