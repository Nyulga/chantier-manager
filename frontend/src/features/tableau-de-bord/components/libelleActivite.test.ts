// Tests des libellés du fil d'activité : un texte par transition, selon qui a agi.
import { expect, it } from 'vitest';

import type { EntreeActivite } from '../services/useActiviteRecente';
import { libelleActivite } from './libelleActivite';

/** Un composant ne peut pas importer les fabriques des services : l'entrée est écrite ici. */
function entree(surcharges: Partial<EntreeActivite> = {}): EntreeActivite {
  return {
    etape_id: 'etape',
    chantier_id: 'chantier',
    titre_etape: 'Pose des meubles',
    role: 'ouvrier',
    ancien_statut: 'en_cours',
    nouveau_statut: 'terminee_a_valider',
    date: '2026-11-21T17:42:00+01:00',
    commentaire: null,
    ...surcharges,
  };
}

/** Le profil courant est toujours l'autre rôle : la phrase reste à la troisième personne. */
it.each([
  {
    ancien_statut: 'a_faire',
    nouveau_statut: 'en_cours',
    role: 'ouvrier',
    profil: 'chef',
    quoi: 'a démarré « Pose des meubles »',
  },
  {
    ancien_statut: 'en_cours',
    nouveau_statut: 'terminee_a_valider',
    role: 'ouvrier',
    profil: 'chef',
    quoi: 'a signalé « Pose des meubles » terminée',
  },
  {
    ancien_statut: 'terminee_a_valider',
    nouveau_statut: 'validee',
    role: 'chef',
    profil: 'ouvrier',
    quoi: 'a validé « Pose des meubles »',
  },
  {
    ancien_statut: 'terminee_a_valider',
    nouveau_statut: 'en_cours',
    role: 'chef',
    profil: 'ouvrier',
    quoi: 'a refusé « Pose des meubles »',
  },
] as const)('écrit la transition $ancien_statut vers $nouveau_statut', (cas) => {
  const { quoi } = libelleActivite(entree(cas), cas.profil);

  expect(quoi).toBe(cas.quoi);
});

it('joint le motif au refus', () => {
  const refus = entree({
    ancien_statut: 'terminee_a_valider',
    nouveau_statut: 'en_cours',
    role: 'chef',
    commentaire: 'Reprise côté nord',
  });

  expect(libelleActivite(refus, 'ouvrier').quoi).toBe(
    'a refusé « Pose des meubles » : Reprise côté nord',
  );
});

it("appelle « Le chef » ou « L'ouvrier » la personne qui a agi", () => {
  expect(libelleActivite(entree({ role: 'chef' }), 'ouvrier').qui).toBe('Le chef');
  expect(libelleActivite(entree({ role: 'ouvrier' }), 'chef').qui).toBe("L'ouvrier");
});

it('écrit « Tu » et conjugue à la deuxième personne quand le rôle est celui du profil courant', () => {
  const validation = entree({
    role: 'chef',
    ancien_statut: 'terminee_a_valider',
    nouveau_statut: 'validee',
  });

  expect(libelleActivite(validation, 'chef')).toMatchObject({
    qui: 'Tu',
    quoi: 'as validé « Pose des meubles »',
  });
});

it('donne les initiales du rôle', () => {
  expect(libelleActivite(entree({ role: 'chef' }), 'ouvrier').initiales).toBe('CH');
  expect(libelleActivite(entree({ role: 'ouvrier' }), 'chef').initiales).toBe('OU');
});

it('retombe sur une phrase neutre pour une transition inconnue', () => {
  const inconnue = entree({ ancien_statut: 'validee', nouveau_statut: 'a_faire' });

  expect(libelleActivite(inconnue, 'chef').quoi).toBe('a modifié « Pose des meubles »');
});
