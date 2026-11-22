// Formulaire de création d'un chantier : les champs de saisie et le bouton d'envoi.
import { useState } from 'react';

import { Alerte, Bouton, Champ, Formulaire } from '@/ui';

import type { SaisieChantier } from '../services/useCreerChantier';

type FormulaireChantierProps = {
  readonly onSoumettre: (saisie: SaisieChantier) => void;
  readonly enCours: boolean;
  readonly erreur?: string | undefined;
};

type DescriptionChamp = {
  readonly cle: keyof SaisieChantier;
  readonly libelle: string;
  readonly type?: 'text' | 'date' | 'number';
};

/** Les champs, dans l'ordre d'affichage : le formulaire s'étend en ajoutant une ligne ici. */
const CHAMPS: readonly DescriptionChamp[] = [
  { cle: 'nom', libelle: 'Nom du chantier' },
  { cle: 'voie', libelle: 'Voie' },
  { cle: 'codePostal', libelle: 'Code postal' },
  { cle: 'ville', libelle: 'Ville' },
  { cle: 'client', libelle: 'Client' },
  { cle: 'dateDebut', libelle: 'Date de début', type: 'date' },
  { cle: 'echeance', libelle: 'Échéance', type: 'date' },
  { cle: 'budget', libelle: 'Budget (en euros)', type: 'number' },
];

const SAISIE_VIDE: SaisieChantier = {
  nom: '',
  voie: '',
  codePostal: '',
  ville: '',
  client: '',
  dateDebut: '',
  echeance: '',
  budget: '',
};

/**
 * Formulaire contrôlé. Il ne vérifie rien : la saisie part telle quelle, et c'est l'API qui
 * répond 422 si elle est invalide. Le message s'affiche juste au-dessus du bouton d'envoi : sur
 * mobile, le formulaire est long et une alerte en haut de page resterait hors de l'écran.
 */
export function FormulaireChantier({ onSoumettre, enCours, erreur }: FormulaireChantierProps) {
  const [saisie, setSaisie] = useState<SaisieChantier>(SAISIE_VIDE);

  return (
    <Formulaire
      onSubmit={() => {
        onSoumettre(saisie);
      }}
    >
      {CHAMPS.map(({ cle, libelle, type }) => (
        <Champ
          key={cle}
          libelle={libelle}
          type={type ?? 'text'}
          valeur={saisie[cle]}
          requis
          onChange={(valeur) => {
            setSaisie({ ...saisie, [cle]: valeur });
          }}
        />
      ))}
      {erreur !== undefined && <Alerte variante="erreur">{erreur}</Alerte>}
      <Bouton type="submit" disabled={enCours}>
        Créer le chantier
      </Bouton>
    </Formulaire>
  );
}
