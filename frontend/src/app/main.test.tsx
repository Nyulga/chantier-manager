// Tests du point d'entrée : montage dans `#root`, et erreur claire si l'élément est absent.
import { screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';

afterEach(() => {
  document.body.innerHTML = '';
  vi.resetModules();
});

it("monte l'application dans l'élément racine de la page", async () => {
  document.body.innerHTML = '<div id="root"></div>';

  await import('./main');

  expect(await screen.findByRole('heading', { level: 1, name: 'Chantier Manager' })).toBeVisible();
});

it("échoue avec un message clair si l'élément racine est absent", async () => {
  await expect(import('./main')).rejects.toThrow("L'élément #root est introuvable");
});
