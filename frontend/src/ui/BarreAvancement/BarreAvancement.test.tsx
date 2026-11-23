// Tests du composant `BarreAvancement` : rôle progressbar, valeur et texte « x / y étapes · z % ».
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';

import { verifierAccessibilite } from '@/test/verifierAccessibilite';
import { BarreAvancement } from './BarreAvancement';

it('expose une barre de progression avec sa valeur en pourcentage', () => {
  render(<BarreAvancement pourcentage={75} etapesValidees={3} etapesTotal={4} />);

  const barre = screen.getByRole('progressbar', { name: 'Avancement' });

  expect(barre).toHaveAttribute('aria-valuenow', '75');
  expect(barre).toHaveAttribute('aria-valuemin', '0');
  expect(barre).toHaveAttribute('aria-valuemax', '100');
});

it('affiche toujours le texte « x / y étapes · z % »', () => {
  render(<BarreAvancement pourcentage={75} etapesValidees={3} etapesTotal={4} />);

  expect(screen.getByText('3 / 4 étapes · 75 %')).toBeVisible();
});

it('écrit « étape » au singulier quand il y en a une seule', () => {
  render(<BarreAvancement pourcentage={0} etapesValidees={0} etapesTotal={1} />);

  expect(screen.getByText('0 / 1 étape · 0 %')).toBeVisible();
});

it('arrondit le pourcentage affiché sans modifier la valeur reçue', () => {
  render(<BarreAvancement pourcentage={66.67} etapesValidees={2} etapesTotal={3} />);

  expect(screen.getByText('2 / 3 étapes · 67 %')).toBeVisible();
  expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '66.67');
});

it('accepte un libellé accessible propre à la barre', () => {
  render(
    <BarreAvancement
      libelle="Avancement de la villa"
      pourcentage={50}
      etapesValidees={1}
      etapesTotal={2}
    />,
  );

  expect(screen.getByRole('progressbar', { name: 'Avancement de la villa' })).toBeVisible();
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  const { container } = render(
    <BarreAvancement pourcentage={50} etapesValidees={1} etapesTotal={2} />,
  );

  await verifierAccessibilite(container);
});

it("n'affiche que « z % » quand les nombres d'étapes ne sont pas connus", () => {
  render(<BarreAvancement pourcentage={40} />);

  expect(screen.getByText('40 %')).toBeVisible();
  expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '40');
});

it("n'a aucun défaut d'accessibilité sans nombres d'étapes", async () => {
  const { container } = render(<BarreAvancement pourcentage={40} />);

  await verifierAccessibilite(container);
});
