// Tests de la section « Activité récente » : libellés, chantier retrouvé par identifiant, états.
import { screen } from '@testing-library/react';
import { expect, it } from 'vitest';

import { activiteDeTest } from '@/test/activiteDeTest';
import { afficherAvecFournisseurs } from '@/test/afficherAvecFournisseurs';
import { resumeChantierDeTest } from '@/test/resumeChantierDeTest';
import { verifierAccessibilite } from '@/test/verifierAccessibilite';

import { SectionActivite } from './SectionActivite';

const CHANTIER = resumeChantierDeTest({ nom: 'Rénovation cuisine' });
const ENTREE = activiteDeTest({
  chantier_id: CHANTIER.id,
  date: new Date(2026, 10, 21, 17, 42).toISOString(),
});
const CHANTIERS = [CHANTIER];

const MAINTENANT = new Date(2026, 10, 22, 10, 0);

function afficher(props: Partial<Parameters<typeof SectionActivite>[0]> = {}) {
  return afficherAvecFournisseurs(
    <SectionActivite
      entrees={[ENTREE]}
      chantiers={CHANTIERS}
      profil="chef"
      maintenant={MAINTENANT}
      {...props}
    />,
  );
}

it('affiche qui, quoi, puis le nom du chantier et le moment', () => {
  afficher();

  expect(screen.getByRole('listitem')).toHaveTextContent(
    "L'ouvrier a signalé « Pose des meubles » terminée",
  );
  expect(screen.getByRole('listitem')).toHaveTextContent('Rénovation cuisine · hier à 17:42');
});

it('écrit « Tu » quand le rôle est celui du profil courant', () => {
  afficher({ profil: 'ouvrier' });

  expect(screen.getByRole('listitem')).toHaveTextContent('Tu as signalé');
});

it("écrit « Chantier » quand la liste des chantiers n'est pas encore chargée", () => {
  afficher({ chantiers: undefined });

  expect(screen.getByRole('listitem')).toHaveTextContent('Chantier · hier à 17:42');
});

it("dit qu'il n'y a pas encore d'activité quand le fil est vide", () => {
  afficher({ entrees: [] });

  expect(screen.getByText('Aucune activité pour le moment.')).toBeVisible();
});

it("affiche l'erreur de l'API", () => {
  afficher({ entrees: undefined, erreur: 'Le service est indisponible.' });

  expect(screen.getByRole('alert')).toHaveTextContent('Le service est indisponible.');
});

it("annonce le chargement tant que le fil n'est pas reçu", () => {
  afficher({ entrees: undefined });

  expect(screen.getByText("Chargement de l'activité…")).toBeVisible();
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  const { container } = afficher();

  await verifierAccessibilite(container);
});
