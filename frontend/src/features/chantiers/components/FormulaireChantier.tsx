// Formulaire de création d'un chantier : les champs de saisie et le bouton d'envoi.
import { useState } from 'react';

import { Alerte, Bouton, Champ, ChampPiege, Formulaire } from '@/ui';

import type { ErreurApi, SaisieChantier } from '../services/useCreerChantier';

type FormulaireChantierProps = {
  readonly onSoumettre: (saisie: SaisieChantier) => void;
  readonly enCours: boolean;
  /** Erreur de l'API : ses messages par champ s'affichent sous les champs, les autres dans une alerte. */
  readonly erreur?: ErreurApi | null | undefined;
};

type DescriptionChamp = {
  readonly cle: Exclude<keyof SaisieChantier, 'siteWeb'>;
  /** Chemin du champ dans le corps de la requête, tel que l'API le désigne dans ses erreurs. */
  readonly champApi: string;
  readonly libelle: string;
  readonly type?: 'text' | 'date' | 'number';
};

/** Les champs, dans l'ordre d'affichage : le formulaire s'étend en ajoutant une ligne ici. */
const CHAMPS: readonly DescriptionChamp[] = [
  { cle: 'nom', champApi: 'nom', libelle: 'Nom du chantier' },
  { cle: 'voie', champApi: 'adresse.voie', libelle: 'Voie' },
  { cle: 'codePostal', champApi: 'adresse.code_postal', libelle: 'Code postal' },
  { cle: 'ville', champApi: 'adresse.ville', libelle: 'Ville' },
  { cle: 'client', champApi: 'client', libelle: 'Client' },
  { cle: 'dateDebut', champApi: 'date_debut', libelle: 'Date de début', type: 'date' },
  { cle: 'echeance', champApi: 'echeance', libelle: 'Échéance', type: 'date' },
  { cle: 'budget', champApi: 'budget', libelle: 'Budget (en euros)', type: 'number' },
];

/** Les champs que le formulaire affiche : le reste des erreurs de l'API va dans l'alerte globale. */
const CHAMPS_API = CHAMPS.map(({ champApi }) => champApi);

const SAISIE_VIDE: SaisieChantier = {
  nom: '',
  voie: '',
  codePostal: '',
  ville: '',
  client: '',
  dateDebut: '',
  echeance: '',
  budget: '',
  siteWeb: '',
};

/**
 * Formulaire contrôlé. Il ne vérifie rien : la saisie part telle quelle, et c'est l'API qui
 * répond 422 si elle est invalide. Chaque message de l'API s'affiche sous son champ ; ce qui ne
 * vise aucun champ affiché va dans une alerte juste au-dessus du bouton d'envoi : sur mobile, le
 * formulaire est long et une alerte en haut de page resterait hors de l'écran.
 */
export function FormulaireChantier({ onSoumettre, enCours, erreur }: FormulaireChantierProps) {
  const [saisie, setSaisie] = useState<SaisieChantier>(SAISIE_VIDE);
  const messageGlobal = erreur?.messageGlobal(CHAMPS_API);

  return (
    <Formulaire
      onSubmit={() => {
        onSoumettre(saisie);
      }}
    >
      {CHAMPS.map(({ cle, champApi, libelle, type }) => (
        <Champ
          key={cle}
          libelle={libelle}
          type={type ?? 'text'}
          valeur={saisie[cle]}
          erreur={erreur?.messageDuChamp(champApi)}
          requis
          onChange={(valeur) => {
            setSaisie({ ...saisie, [cle]: valeur });
          }}
        />
      ))}
      <ChampPiege
        valeur={saisie.siteWeb}
        onChange={(siteWeb) => {
          setSaisie({ ...saisie, siteWeb });
        }}
      />
      {messageGlobal !== undefined && <Alerte>{messageGlobal}</Alerte>}
      <Bouton type="submit" disabled={enCours}>
        Créer le chantier
      </Bouton>
    </Formulaire>
  );
}
