// Tests de la section « Mes chantiers » : aperçu limité, lien vers la liste, et états de chargement.
import { screen, within } from '@testing-library/react';
import { expect, it } from 'vitest';

import { afficherAvecFournisseurs } from '@/ui/test/afficherAvecFournisseurs';
import { verifierAccessibilite } from '@/ui/test/verifierAccessibilite';

import type { Chantier } from '../services/useChantiers';
import { SectionMesChantiers } from './SectionMesChantiers';

/** Un composant ne peut pas importer les fabriques des services : le chantier est écrit ici. */
function chantier(surcharges: Partial<Chantier> = {}): Chantier {
  return {
    id: 'chantier-1',
    nom: 'Rénovation cuisine',
    adresse: { voie: '12 rue des Tanneurs', code_postal: '69007', ville: 'Lyon' },
    client: 'Client',
    date_debut: '2026-03-02',
    echeance: '2027-01-15',
    budget: null,
    avancement: 50,
    peut_ajouter_etape: false,
    etapes_validees: 3,
    etapes_total: 6,
    etapes_a_valider: 0,
    jours_restants: 54,
    en_retard: false,
    ...surcharges,
  };
}

function afficher(props: Parameters<typeof SectionMesChantiers>[0]) {
  return afficherAvecFournisseurs(<SectionMesChantiers {...props} />);
}

it('affiche au plus quatre cartes et un lien vers tous les chantiers', () => {
  const chantiers = Array.from({ length: 6 }, (_, i) =>
    chantier({ id: `chantier-${String(i)}`, nom: `Chantier numéro ${String(i)}` }),
  );

  afficher({ chantiers });

  expect(screen.getAllByRole('heading', { level: 3 })).toHaveLength(4);
  expect(screen.getByRole('link', { name: 'Voir les 6 chantiers' })).toHaveAttribute(
    'href',
    '/chantiers',
  );
});

it('affiche les puces « à valider » et « en retard » avec le délai en toutes lettres', () => {
  afficher({
    chantiers: [chantier({ etapes_a_valider: 2, en_retard: true, jours_restants: 4 })],
  });

  const region = screen.getByRole('region', { name: 'Mes chantiers' });
  expect(within(region).getByText('2 à valider')).toBeVisible();
  expect(within(region).getByText('En retard')).toBeVisible();
  expect(within(region).getByText('En retard de 4 jours')).toBeVisible();
  expect(within(region).getByText('3 / 6 étapes · 50 %')).toBeVisible();
  expect(within(region).getByText('15/01/2027')).toBeVisible();
});

it('n’affiche aucune puce pour un chantier sans étape à valider ni retard', () => {
  afficher({ chantiers: [chantier()] });

  expect(screen.queryByText(/à valider/)).not.toBeInTheDocument();
  expect(screen.getByText('J-54')).toBeVisible();
});

it('dit qu’il n’y a aucun chantier quand la liste est vide', () => {
  afficher({ chantiers: [] });

  expect(screen.getByText('Aucun chantier pour le moment.')).toBeVisible();
});

it('affiche l’erreur de l’API', () => {
  afficher({ chantiers: undefined, erreur: 'Le service est indisponible.' });

  expect(screen.getByRole('alert')).toHaveTextContent('Le service est indisponible.');
});

it('annonce le chargement tant que la liste n’est pas reçue', () => {
  afficher({ chantiers: undefined });

  expect(screen.getByText('Chargement des chantiers…')).toBeVisible();
});

it('n’a aucun défaut d’accessibilité détectable par axe', async () => {
  const { container } = afficher({ chantiers: [chantier()] });

  await verifierAccessibilite(container);
});
