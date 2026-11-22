// Section « À valider » du tableau de bord : les étapes signalées terminées, avec leurs actions.
import { Alerte, BlocAValider, formaterMoment, LigneAValider, Section, Texte } from '@/ui';

import type { Chantier } from '../services/useChantiers';
import type { EtapeAValider } from '../services/useEtapesAValider';
import { ActionsAValider } from './ActionsAValider';
import { nomDuChantier } from './nomDuChantier';

type SectionAValiderProps = {
  /** `undefined` tant que la liste n'est pas chargée. */
  readonly etapes: readonly EtapeAValider[] | undefined;
  readonly erreurChargement?: string | undefined;
  readonly chantiers: readonly Chantier[] | undefined;
  readonly maintenant: Date;
  readonly enCours: boolean;
  /** Erreur de la dernière validation, avec l'étape concernée : seule sa ligne l'affiche. */
  readonly erreurValidation?: { readonly etapeId: string; readonly message: string } | undefined;
  readonly onValider: (etape: EtapeAValider) => void;
};

const TITRE = 'À valider';

/** Texte du signalement : l'API peut ne pas donner de date sur une donnée incohérente. */
function signalement(etape: EtapeAValider, maintenant: Date): string {
  return etape.signalee_le === null
    ? 'Signalée terminée'
    : `Signalée ${formaterMoment(etape.signalee_le, maintenant)}`;
}

/**
 * Le bloc jaune et rayé n'apparaît que s'il y a des étapes : sans action à mener, le jaune
 * contredirait la règle d'or de Balise. Les actions de chaque ligne sont dans `ActionsAValider`.
 */
export function SectionAValider({
  etapes,
  erreurChargement,
  chantiers,
  maintenant,
  enCours,
  erreurValidation,
  onValider,
}: SectionAValiderProps) {
  if (erreurChargement !== undefined) {
    return (
      <Section titre={TITRE}>
        <Alerte variante="erreur">{erreurChargement}</Alerte>
      </Section>
    );
  }
  if (etapes === undefined) {
    return (
      <Section titre={TITRE}>
        <Texte variante="secondaire">Chargement des étapes à valider…</Texte>
      </Section>
    );
  }
  if (etapes.length === 0) {
    return (
      <Section titre={TITRE}>
        <Texte>
          Rien à valider pour le moment. Les étapes que tes ouvriers signalent terminées
          apparaîtront ici.
        </Texte>
      </Section>
    );
  }

  return (
    <BlocAValider
      titre={TITRE}
      compteur={etapes.length}
      sousTitre="Étapes signalées terminées par tes ouvriers"
    >
      {etapes.map((etape) => (
        <LigneAValider
          key={etape.id}
          titre={etape.titre}
          contexte={nomDuChantier(chantiers, etape.chantier_id)}
          signalement={signalement(etape, maintenant)}
          erreur={erreurValidation?.etapeId === etape.id ? erreurValidation.message : undefined}
          actions={<ActionsAValider etape={etape} enCours={enCours} onValider={onValider} />}
        />
      ))}
    </BlocAValider>
  );
}
