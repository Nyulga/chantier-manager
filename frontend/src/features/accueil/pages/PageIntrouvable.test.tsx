// Tests de la page 404 : message clair et retour vers la liste des chantiers.
import { screen } from '@testing-library/react';
import { Route, Routes } from 'react-router';
import { expect, it } from 'vitest';

import { afficherAvecFournisseurs } from '@/ui/test/afficherAvecFournisseurs';
import { verifierAccessibilite } from '@/ui/test/verifierAccessibilite';

import { PageIntrouvable } from './PageIntrouvable';

function afficherPage() {
  return afficherAvecFournisseurs(
    <Routes>
      <Route path="*" element={<PageIntrouvable />} />
    </Routes>,
    '/n-importe-quoi',
  );
}

it('explique que la page n’existe pas et propose de revenir aux chantiers', () => {
  afficherPage();

  expect(screen.getByRole('heading', { level: 2, name: 'Page introuvable' })).toBeVisible();
  expect(screen.getByRole('link', { name: 'Retour aux chantiers' })).toHaveAttribute('href', '/');
});

it('n’a aucun défaut d’accessibilité détectable par axe', async () => {
  const { container } = afficherPage();

  await verifierAccessibilite(container);
});
