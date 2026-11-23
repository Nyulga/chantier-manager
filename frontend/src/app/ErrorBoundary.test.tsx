// Tests de la barrière d'erreurs : une erreur de rendu donne une page d'erreur, jamais une page blanche.
import { fireEvent, render, screen } from '@testing-library/react';
import { afterEach, expect, it, vi } from 'vitest';

import { ErrorBoundary } from './ErrorBoundary';

afterEach(() => {
  vi.restoreAllMocks();
});

/** Composant de test qui plante au rendu, comme le ferait une donnée inattendue. */
function Plante(): never {
  throw new Error('Rendu impossible');
}

/** React journalise l'erreur attrapée : on évite ce bruit dans la sortie des tests. */
function faireTaireLeJournal() {
  vi.spyOn(console, 'error').mockImplementation(() => undefined);
}

it('affiche ses enfants tant que rien ne plante', () => {
  render(
    <ErrorBoundary rechargerPage={vi.fn()}>
      <p>Contenu de la page</p>
    </ErrorBoundary>,
  );

  expect(screen.getByText('Contenu de la page')).toBeVisible();
  expect(
    screen.queryByRole('heading', { name: 'Une erreur est survenue' }),
  ).not.toBeInTheDocument();
});

it("remplace une page qui plante par la page d'erreur, avec un bouton « Recharger »", () => {
  faireTaireLeJournal();

  render(
    <ErrorBoundary rechargerPage={vi.fn()}>
      <Plante />
    </ErrorBoundary>,
  );

  expect(screen.getByRole('heading', { level: 1, name: 'Une erreur est survenue' })).toBeVisible();
  expect(screen.getByRole('button', { name: 'Recharger' })).toBeVisible();
});

it('recharge la page quand on appuie sur « Recharger »', () => {
  faireTaireLeJournal();
  const rechargerPage = vi.fn();
  render(
    <ErrorBoundary rechargerPage={rechargerPage}>
      <Plante />
    </ErrorBoundary>,
  );

  fireEvent.click(screen.getByRole('button', { name: 'Recharger' }));

  expect(rechargerPage).toHaveBeenCalledOnce();
});
