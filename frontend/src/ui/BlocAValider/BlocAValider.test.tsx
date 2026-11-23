// Tests du `BlocAValider` et de la `LigneAValider` : le bloc des étapes qui attendent le chef.
import { render, screen, within } from '@testing-library/react';
import { createRef } from 'react';
import { expect, it } from 'vitest';

import { Alerte } from '../Alerte/Alerte';
import { LigneAValider } from '../LigneAValider/LigneAValider';
import { verifierAccessibilite } from '@/test/verifierAccessibilite';
import { BlocAValider } from './BlocAValider';

function afficher() {
  return render(
    <BlocAValider
      titre="À valider"
      compteur={2}
      sousTitre="Étapes signalées terminées"
      alerte={<Alerte>Impossible de valider « Faïence ».</Alerte>}
    >
      <LigneAValider
        titre="Pose des meubles"
        contexte="Rénovation cuisine"
        signalement="Signalée hier à 17:42"
        actions={<button type="button">Valider</button>}
      />
      <LigneAValider
        titre="Faïence"
        contexte="Salle de bain"
        signalement="Signalée lundi"
        actions={null}
      />
    </BlocAValider>,
  );
}

it('est une région nommée « À valider », avec son compteur et son sous-titre', () => {
  afficher();

  const region = screen.getByRole('region', { name: 'À valider' });
  expect(within(region).getByText('2')).toBeVisible();
  expect(within(region).getByText('Étapes signalées terminées')).toBeVisible();
});

it('liste les étapes avec leur contexte, leur signalement et leurs actions', () => {
  afficher();

  const [premiere, seconde] = screen.getAllByRole('listitem');
  expect(screen.getAllByRole('listitem')).toHaveLength(2);
  expect(premiere).toHaveTextContent('Pose des meubles');
  expect(premiere).toHaveTextContent('Rénovation cuisine');
  expect(premiere).toHaveTextContent('Signalée hier à 17:42');
  expect(premiere).toContainElement(screen.getByRole('button', { name: 'Valider' }));
  expect(seconde).toHaveTextContent('Faïence');
});

it("affiche l'alerte au niveau du bloc, hors des lignes", () => {
  afficher();

  const alerte = screen.getByRole('alert');
  expect(alerte).toHaveTextContent('Impossible de valider « Faïence ».');
  expect(within(screen.getByRole('region', { name: 'À valider' })).getByRole('alert')).toBe(alerte);
  for (const ligne of screen.getAllByRole('listitem')) {
    expect(ligne).not.toContainElement(alerte);
  }
});

it('rend son titre focalisable par programme quand une référence lui est donnée', () => {
  const reference = createRef<HTMLHeadingElement>();
  render(
    <BlocAValider titre="À valider" compteur={1} sousTitre="Sous-titre" refTitre={reference}>
      <LigneAValider titre="Pose" contexte="Cuisine" signalement="Hier" actions={null} />
    </BlocAValider>,
  );

  reference.current?.focus();

  expect(screen.getByRole('heading', { level: 2, name: 'À valider' })).toHaveFocus();
});

it('affiche « + » après le compteur quand la liste est coupée', () => {
  render(
    <BlocAValider titre="À valider" compteur={50} compteurAuMoins sousTitre="Sous-titre">
      <LigneAValider titre="Pose" contexte="Cuisine" signalement="Hier" actions={null} />
    </BlocAValider>,
  );

  expect(screen.getByText('50+')).toBeVisible();
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  const { container } = afficher();

  await verifierAccessibilite(container);
});
