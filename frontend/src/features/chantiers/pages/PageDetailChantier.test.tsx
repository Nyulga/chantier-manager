// Tests de la page « détail du chantier » : informations, budget visible ou non, 404 et contexte.
import { screen } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { Route, Routes, useOutletContext } from 'react-router';
import { expect, it } from 'vitest';

import { afficherAvecFournisseurs } from '@/ui/test/afficherAvecFournisseurs';
import { installerServeurApi } from '@/ui/test/serveurApiSimule';
import { verifierAccessibilite } from '@/ui/test/verifierAccessibilite';

import { chantierDeTest } from '../services/chantierDeTest';
import type { Chantier } from '../services/useChantiers';
import { PageDetailChantier } from './PageDetailChantier';

const serveur = installerServeurApi();

/** Page enfant factice : montre ce que le détail transmet à la page des étapes. */
function EtapesFactices() {
  const contexte = useOutletContext<{ chantierId: string; peutAjouterEtape: boolean }>();
  return <p>{`Étapes de ${contexte.chantierId} (ajout : ${String(contexte.peutAjouterEtape)})`}</p>;
}

function afficherPage(chantier: Chantier) {
  serveur.use(http.get(`/api/chantiers/${chantier.id}`, () => HttpResponse.json(chantier)));
  return afficherAvecFournisseurs(
    <Routes>
      <Route path="/chantiers/:id" element={<PageDetailChantier />}>
        <Route index element={<EtapesFactices />} />
      </Route>
    </Routes>,
    `/chantiers/${chantier.id}`,
  );
}

it('affiche les informations du chantier, dont le budget formaté', async () => {
  afficherPage(chantierDeTest());

  expect(
    await screen.findByRole('heading', { level: 2, name: 'Rénovation de la mairie' }),
  ).toBeVisible();
  expect(screen.getByText('12 rue des Lilas, 69003 Lyon')).toBeVisible();
  expect(screen.getByText('Client : Mairie de Lyon')).toBeVisible();
  expect(screen.getByText('Du 02/03/2026 au 30/09/2026')).toBeVisible();
  expect(screen.getByText(/^Budget : 18\s450,00\s€$/)).toBeVisible();
});

it('n’affiche pas le budget quand l’API ne le donne pas', async () => {
  afficherPage(chantierDeTest({ budget: null }));

  await screen.findByRole('heading', { level: 2 });
  expect(screen.queryByText(/Budget/)).not.toBeInTheDocument();
});

it('transmet à la page des étapes l’identifiant et le droit d’ajout venus de l’API', async () => {
  const chantier = chantierDeTest({ peut_ajouter_etape: false });
  afficherPage(chantier);

  expect(await screen.findByText(`Étapes de ${chantier.id} (ajout : false)`)).toBeVisible();
});

it('affiche le message de l’API quand le chantier n’existe pas', async () => {
  serveur.use(
    http.get('/api/chantiers/inconnu', () =>
      HttpResponse.json(
        { status: 404, detail: 'Chantier introuvable.' },
        { status: 404, headers: { 'Content-Type': 'application/problem+json' } },
      ),
    ),
  );
  afficherAvecFournisseurs(
    <Routes>
      <Route path="/chantiers/:id" element={<PageDetailChantier />} />
    </Routes>,
    '/chantiers/inconnu',
  );

  expect(await screen.findByRole('alert')).toHaveTextContent('Chantier introuvable.');
});

it('n’a aucun défaut d’accessibilité détectable par axe', async () => {
  const { container } = afficherPage(chantierDeTest());
  await screen.findByRole('heading', { level: 2 });

  await verifierAccessibilite(container);
});
