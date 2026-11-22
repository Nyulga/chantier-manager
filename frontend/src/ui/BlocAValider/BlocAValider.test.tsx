// Tests du `BlocAValider` et de la `LigneAValider` : le bloc des étapes qui attendent le chef.
import { render, screen, within } from '@testing-library/react';
import { expect, it } from 'vitest';

import { LigneAValider } from '../LigneAValider/LigneAValider';
import { verifierAccessibilite } from '../test/verifierAccessibilite';
import { BlocAValider } from './BlocAValider';

function afficher() {
  return render(
    <BlocAValider
      titre="À valider"
      compteur={2}
      sousTitre="Étapes signalées terminées par tes ouvriers"
    >
      <LigneAValider
        titre="Pose des meubles"
        contexte="Rénovation cuisine"
        signalement="Signalée hier à 17:42"
        actions={<button type="button">Valider</button>}
        erreur="Cette étape a déjà changé de statut."
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
  expect(within(region).getByText('Étapes signalées terminées par tes ouvriers')).toBeVisible();
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

it('affiche l’erreur de l’API près de l’action de la ligne concernée', () => {
  afficher();

  const [premiere, seconde] = screen.getAllByRole('listitem');
  expect(premiere).toContainElement(screen.getByRole('alert'));
  expect(screen.getByRole('alert')).toHaveTextContent('Cette étape a déjà changé de statut.');
  expect(seconde).not.toContainElement(screen.getByRole('alert'));
});

it('n’a aucun défaut d’accessibilité détectable par axe', async () => {
  const { container } = afficher();

  await verifierAccessibilite(container);
});
