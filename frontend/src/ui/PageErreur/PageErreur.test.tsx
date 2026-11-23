// Tests de la page d'erreur : elle explique le problème en français et propose de recharger.
import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';

import { verifierAccessibilite } from '@/test/verifierAccessibilite';

import { PageErreur } from './PageErreur';

it('explique que quelque chose a mal tourné, en français et en tutoyant', () => {
  render(<PageErreur onRecharger={vi.fn()} />);

  expect(screen.getByRole('heading', { level: 1, name: 'Une erreur est survenue' })).toBeVisible();
  expect(screen.getByText(/Recharge la page/)).toBeVisible();
});

it('appelle onRecharger quand on appuie sur « Recharger »', () => {
  const onRecharger = vi.fn();
  render(<PageErreur onRecharger={onRecharger} />);

  fireEvent.click(screen.getByRole('button', { name: 'Recharger' }));

  expect(onRecharger).toHaveBeenCalledOnce();
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  const { container } = render(
    <main>
      <PageErreur onRecharger={vi.fn()} />
    </main>,
  );

  await verifierAccessibilite(container);
});
