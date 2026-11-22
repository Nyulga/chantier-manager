// Tests de l'en-tête commun : titre de l'application, sélecteur de profil et contenu de la page.
import { fireEvent, screen } from '@testing-library/react';
import { Route, Routes } from 'react-router';
import { afterEach, expect, it } from 'vitest';

import { afficherAvecFournisseurs } from '@/ui/test/afficherAvecFournisseurs';
import { verifierAccessibilite } from '@/ui/test/verifierAccessibilite';

import { LayoutApplication } from './LayoutApplication';

afterEach(() => {
  localStorage.clear();
});

function afficherLayout() {
  return afficherAvecFournisseurs(
    <Routes>
      <Route element={<LayoutApplication />}>
        <Route index element={<p>Contenu de la page</p>} />
      </Route>
    </Routes>,
  );
}

it('affiche le titre de l’application, le sélecteur de profil et la page', () => {
  afficherLayout();

  expect(screen.getByRole('heading', { level: 1, name: 'Chantier Manager' })).toBeVisible();
  expect(screen.getByRole('radio', { name: 'Chef' })).toBeChecked();
  expect(screen.getByText('Contenu de la page')).toBeVisible();
});

it('change de profil quand l’utilisateur choisit Ouvrier', () => {
  afficherLayout();

  fireEvent.click(screen.getByRole('radio', { name: 'Ouvrier' }));

  expect(screen.getByRole('radio', { name: 'Ouvrier' })).toBeChecked();
  expect(localStorage.getItem('chantier-manager.profil')).toBe('ouvrier');
});

it('n’a aucun défaut d’accessibilité détectable par axe', async () => {
  const { container } = afficherLayout();

  await verifierAccessibilite(container);
});
