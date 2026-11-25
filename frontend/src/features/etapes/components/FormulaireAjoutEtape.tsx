// Formulaire d'ajout d'une étape : un titre et un bouton.
import { useState } from 'react';

import { Alerte, Bouton, Champ, ChampPiege, Formulaire } from '@/ui';

import type { ErreurApi, SaisieEtape } from '../services/useAjouterEtape';

type FormulaireAjoutEtapeProps = {
  readonly enCours: boolean;
  /** Erreur de l'API : son message sur le titre s'affiche sous le champ, les autres dans une alerte. */
  readonly erreur?: ErreurApi | null | undefined;
  /** `apresSucces` est appelé quand l'API a accepté l'étape : le champ est alors vidé. */
  readonly onAjouter: (saisie: SaisieEtape, apresSucces: () => void) => void;
};

/** Nom du champ dans le corps de la requête, tel que l'API le désigne dans ses erreurs. */
const CHAMP_TITRE = 'titre';

/** Le titre est vérifié par l'API (422 si invalide) : le formulaire envoie ce qui est saisi. */
export function FormulaireAjoutEtape({ enCours, erreur, onAjouter }: FormulaireAjoutEtapeProps) {
  const [titre, setTitre] = useState('');
  const [siteWeb, setSiteWeb] = useState('');
  const messageGlobal = erreur?.messageGlobal([CHAMP_TITRE]);

  return (
    <Formulaire
      onSubmit={() => {
        onAjouter({ titre, siteWeb }, () => {
          setTitre('');
        });
      }}
    >
      <Champ
        libelle="Titre de l'étape"
        valeur={titre}
        onChange={setTitre}
        erreur={erreur?.messageDuChamp(CHAMP_TITRE)}
        requis
      />
      <ChampPiege valeur={siteWeb} onChange={setSiteWeb} />
      {messageGlobal !== undefined && <Alerte>{messageGlobal}</Alerte>}
      <Bouton type="submit" disabled={enCours}>
        Ajouter l&apos;étape
      </Bouton>
    </Formulaire>
  );
}
