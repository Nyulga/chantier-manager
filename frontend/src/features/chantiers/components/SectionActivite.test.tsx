// Tests de la section « Activité récente » : libellés, chantier retrouvé par identifiant, états.
import { screen } from '@testing-library/react';
import { expect, it } from 'vitest';

import { afficherAvecFournisseurs } from '@/ui/test/afficherAvecFournisseurs';
import { verifierAccessibilite } from '@/ui/test/verifierAccessibilite';

import type { EntreeActivite } from '../services/useActiviteRecente';
import type { Chantier } from '../services/useChantiers';
import { SectionActivite } from './SectionActivite';

/** Un composant ne peut pas importer les fabriques des services : les données sont écrites ici. */
const ENTREE: EntreeActivite = {
  etape_id: 'etape',
  chantier_id: 'chantier-1',
  titre_etape: 'Pose des meubles',
  role: 'ouvrier',
  ancien_statut: 'en_cours',
  nouveau_statut: 'terminee_a_valider',
  date: new Date(2026, 10, 21, 17, 42).toISOString(),
  commentaire: null,
};

const CHANTIERS: readonly Chantier[] = [
  {
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
  },
];

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
    'L’ouvrier a signalé « Pose des meubles » terminée',
  );
  expect(screen.getByRole('listitem')).toHaveTextContent('Rénovation cuisine · hier à 17:42');
});

it('écrit « Toi » quand le rôle est celui du profil courant', () => {
  afficher({ profil: 'ouvrier' });

  expect(screen.getByRole('listitem')).toHaveTextContent('Toi as signalé');
});

it('écrit « Chantier » quand la liste des chantiers n’est pas encore chargée', () => {
  afficher({ chantiers: undefined });

  expect(screen.getByRole('listitem')).toHaveTextContent('Chantier · hier à 17:42');
});

it('dit qu’il n’y a pas encore d’activité quand le fil est vide', () => {
  afficher({ entrees: [] });

  expect(screen.getByText('Aucune activité pour le moment.')).toBeVisible();
});

it('affiche l’erreur de l’API', () => {
  afficher({ entrees: undefined, erreur: 'Le service est indisponible.' });

  expect(screen.getByRole('alert')).toHaveTextContent('Le service est indisponible.');
});

it('annonce le chargement tant que le fil n’est pas reçu', () => {
  afficher({ entrees: undefined });

  expect(screen.getByText('Chargement de l’activité…')).toBeVisible();
});

it('n’a aucun défaut d’accessibilité détectable par axe', async () => {
  const { container } = afficher();

  await verifierAccessibilite(container);
});
