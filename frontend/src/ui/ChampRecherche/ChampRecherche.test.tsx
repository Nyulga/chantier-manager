// Tests du `ChampRecherche` : un champ de recherche désactivé, avec la mention « Bientôt ».
import { render, screen } from '@testing-library/react';
import { expect, it } from 'vitest';

import { verifierAccessibilite } from '@/test/verifierAccessibilite';
import { ChampRecherche } from './ChampRecherche';

function afficher() {
  return render(<ChampRecherche libelle="Rechercher un chantier" />);
}

it('est un champ de recherche désactivé, nommé par son libellé', () => {
  afficher();

  expect(screen.getByRole('searchbox', { name: 'Rechercher un chantier' })).toBeDisabled();
});

it('affiche la mention « Bientôt »', () => {
  afficher();

  expect(screen.getByText('Bientôt')).toBeVisible();
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  const { container } = afficher();

  await verifierAccessibilite(container);
});
