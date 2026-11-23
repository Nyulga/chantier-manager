// Tests de la `CarteChantier` : nom, adresse, avancement, échéance et délai, le tout cliquable.
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router';
import { expect, it } from 'vitest';

import { PuceChantier } from '../PuceChantier/PuceChantier';
import { verifierAccessibilite } from '@/test/verifierAccessibilite';
import { CarteChantier } from './CarteChantier';

function afficher(enRetard = false) {
  return render(
    <MemoryRouter>
      <CarteChantier
        nom="Rénovation cuisine Martin"
        vers="/chantiers/42"
        adresse="12 rue des Tanneurs, 69007 Lyon"
        puces={<PuceChantier variante="a-valider">1 à valider</PuceChantier>}
        etapesValidees={3}
        etapesTotal={6}
        pourcentage={50}
        echeance="15/01/2027"
        delai={enRetard ? 'En retard de 4 jours' : 'J-54'}
        enRetard={enRetard}
      />
    </MemoryRouter>,
  );
}

it('affiche le nom comme titre et comme lien vers le chantier', () => {
  afficher();

  expect(
    screen.getByRole('heading', { level: 3, name: 'Rénovation cuisine Martin' }),
  ).toBeVisible();
  expect(screen.getByRole('link', { name: 'Rénovation cuisine Martin' })).toHaveAttribute(
    'href',
    '/chantiers/42',
  );
});

it("affiche le titre au niveau demandé, pour respecter l'ordre des titres de la page", () => {
  render(
    <MemoryRouter>
      <CarteChantier
        nom="Chantier"
        vers="/chantiers/1"
        adresse="Lyon"
        etapesValidees={0}
        etapesTotal={0}
        pourcentage={0}
        echeance="15/01/2027"
        delai="J-5"
        enRetard={false}
        niveauTitre={2}
      />
    </MemoryRouter>,
  );

  expect(screen.getByRole('heading', { level: 2, name: 'Chantier' })).toBeVisible();
});

it("affiche l'adresse, la puce, l'avancement, l'échéance et le délai", () => {
  afficher();

  expect(screen.getByText('12 rue des Tanneurs, 69007 Lyon')).toBeVisible();
  expect(screen.getByText('1 à valider')).toBeVisible();
  expect(
    screen.getByRole('progressbar', { name: 'Avancement de Rénovation cuisine Martin' }),
  ).toHaveAttribute('aria-valuenow', '50');
  expect(screen.getByText('3 / 6 étapes · 50 %')).toBeVisible();
  expect(screen.getByText('15/01/2027')).toBeVisible();
  expect(screen.getByText('J-54')).toBeVisible();
});

it('écrit le retard en toutes lettres', () => {
  afficher(true);

  expect(screen.getByText('En retard de 4 jours')).toBeVisible();
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  const { container } = afficher();

  await verifierAccessibilite(container);
});
