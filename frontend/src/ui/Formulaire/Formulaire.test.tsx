// Tests du composant `Formulaire` : envoi sans rechargement, validation du navigateur coupée.
import { fireEvent, render, screen } from '@testing-library/react';
import { expect, it, vi } from 'vitest';

import { Bouton } from '../Bouton/Bouton';
import { Champ } from '../Champ/Champ';
import { verifierAccessibilite } from '@/test/verifierAccessibilite';
import { Formulaire } from './Formulaire';

const surChangement = () => undefined;

function afficher(onSubmit: () => void) {
  return render(
    <Formulaire onSubmit={onSubmit}>
      <Champ libelle="Nom" valeur="" onChange={surChangement} requis />
      <Bouton type="submit">Enregistrer</Bouton>
    </Formulaire>,
  );
}

it('appelle onSubmit même si un champ obligatoire est vide (noValidate)', () => {
  const onSubmit = vi.fn();
  afficher(onSubmit);

  // L'API fait autorité : on n'affiche pas les bulles de validation du navigateur.
  fireEvent.click(screen.getByRole('button', { name: 'Enregistrer' }));

  expect(onSubmit).toHaveBeenCalledOnce();
});

it("empêche le rechargement de la page à l'envoi", () => {
  afficher(vi.fn());

  const bouton = screen.getByRole('button', { name: 'Enregistrer' });
  const evenement = new Event('submit', { bubbles: true, cancelable: true });
  bouton.closest('form')?.dispatchEvent(evenement);

  expect(evenement.defaultPrevented).toBe(true);
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  const { container } = afficher(vi.fn());

  await verifierAccessibilite(container);
});
