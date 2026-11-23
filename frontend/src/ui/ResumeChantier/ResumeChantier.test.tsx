// Tests du `ResumeChantier` : la carte du chantier, avec ses puces d'état et son délai écrits à partir de valeurs simples.
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { expect, it } from 'vitest';

import { verifierAccessibilite } from '@/test/verifierAccessibilite';

import { ResumeChantier } from './ResumeChantier';

const RESUME = {
  nom: 'Rénovation cuisine Martin',
  vers: '/chantiers/42',
  adresse: '12 rue des Tanneurs, 69007 Lyon',
  etapesValidees: 3,
  etapesTotal: 6,
  avancement: 50,
  etapesAValider: 0,
  echeance: '2027-01-15',
  joursRestants: 54,
  enRetard: false,
};

function afficher(surcharges: Partial<typeof RESUME> & { niveauTitre?: 2 | 3 } = {}) {
  return render(
    <MemoryRouter>
      <ResumeChantier {...RESUME} {...surcharges} />
    </MemoryRouter>,
  );
}

it("affiche le nom en lien vers le chantier, l'adresse et l'avancement", () => {
  afficher();

  expect(screen.getByRole('link', { name: 'Rénovation cuisine Martin' })).toHaveAttribute(
    'href',
    '/chantiers/42',
  );
  expect(screen.getByText('12 rue des Tanneurs, 69007 Lyon')).toBeVisible();
  expect(
    screen.getByRole('progressbar', { name: 'Avancement de Rénovation cuisine Martin' }),
  ).toHaveAttribute('aria-valuenow', '50');
});

it("met en forme l'échéance et le délai que l'API a calculés", () => {
  afficher();

  expect(screen.getByText('15/01/2027')).toBeVisible();
  expect(screen.getByText('J-54')).toBeVisible();
});

it("écrit le retard en toutes lettres, avec une puce, quand l'API le signale", () => {
  afficher({ enRetard: true, joursRestants: 4 });

  expect(screen.getByText('En retard de 4 jours')).toBeVisible();
  expect(screen.getByText('En retard')).toBeVisible();
});

it('affiche la puce « à valider » avec le compteur, et rien quand il est à zéro', () => {
  const { unmount } = afficher({ etapesAValider: 2 });
  expect(screen.getByText('2 à valider')).toBeVisible();
  unmount();

  afficher({ etapesAValider: 0 });
  expect(screen.queryByText(/à valider/)).not.toBeInTheDocument();
  expect(screen.queryByText('En retard')).not.toBeInTheDocument();
});

it("donne au titre le niveau demandé, 3 par défaut, pour respecter l'ordre des titres de la page", () => {
  const { unmount } = afficher();
  expect(screen.getByRole('heading', { level: 3 })).toBeVisible();
  unmount();

  afficher({ niveauTitre: 2 });
  expect(screen.getByRole('heading', { level: 2 })).toBeVisible();
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  const { container } = afficher({ etapesAValider: 1, enRetard: true, joursRestants: 4 });

  await verifierAccessibilite(container);
});
