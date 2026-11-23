// Section « À valider » du tableau de bord : les étapes signalées terminées, avec leurs actions.
import type { ReactNode } from 'react';

import { Alerte, BlocAValider, Section, Texte } from '@/ui';

import type { ChantierDeListe } from '../services/useChantiers';
import type { EtapeAValider } from '../services/useEtapesAValider';
import { LigneEtapeAValider } from './LigneEtapeAValider';
import { nomDuChantier } from './nomDuChantier';
import { useFocusApresValidation } from './useFocusApresValidation';

type SectionAValiderProps = {
  /** `undefined` tant que la liste n'est pas chargée. */
  readonly etapes: readonly EtapeAValider[] | undefined;
  /** Vrai quand l'API a coupé la liste à son plafond : le compteur affiche alors « 50+ ». */
  readonly tronquee: boolean;
  readonly erreurChargement?: string | undefined;
  readonly chantiers: readonly ChantierDeListe[] | undefined;
  readonly maintenant: Date;
  readonly enCours: boolean;
  /**
   * Erreur de la dernière validation, avec le titre de l'étape concernée. Elle s'affiche au niveau
   * de la section, et non sur la ligne : après un 409 la relecture retire l'étape de la liste, et
   * la ligne (avec son alerte) disparaîtrait avant que l'utilisateur ait pu lire le message.
   */
  readonly erreurValidation?: { readonly titre: string; readonly message: string } | undefined;
  readonly onValider: (etape: EtapeAValider) => void;
};

const TITRE = 'À valider';

/** L'étape est nommée : la ligne a pu disparaître de la liste avant que l'utilisateur lise le message. */
function AlerteValidation({ erreur }: { readonly erreur: { titre: string; message: string } }) {
  return (
    <Alerte>
      Impossible de valider « {erreur.titre} » : {erreur.message}
    </Alerte>
  );
}

/**
 * Le bloc jaune et rayé n'apparaît que s'il y a des étapes : sans action à mener, le jaune
 * contredirait la règle d'or de Balise. Les actions de chaque ligne sont dans `ActionsAValider`.
 */
export function SectionAValider({
  etapes,
  tronquee,
  erreurChargement,
  chantiers,
  maintenant,
  enCours,
  erreurValidation,
  onValider,
}: SectionAValiderProps) {
  const { refTitre, refLigne, memoriser } = useFocusApresValidation(etapes, enCours);

  const dansSection = (contenu: ReactNode) => (
    <Section titre={TITRE} refTitre={refTitre}>
      {contenu}
    </Section>
  );

  if (erreurChargement !== undefined) {
    return dansSection(<Alerte>{erreurChargement}</Alerte>);
  }
  if (etapes === undefined) {
    return dansSection(<Texte variante="secondaire">Chargement des étapes à valider…</Texte>);
  }
  const alerte = erreurValidation && <AlerteValidation erreur={erreurValidation} />;
  if (etapes.length === 0) {
    return dansSection(
      <>
        {alerte}
        <Texte>
          Rien à valider pour le moment. Les étapes signalées terminées apparaîtront ici.
        </Texte>
      </>,
    );
  }

  return (
    <BlocAValider
      titre={TITRE}
      compteur={etapes.length}
      compteurAuMoins={tronquee}
      sousTitre="Étapes signalées terminées"
      refTitre={refTitre}
      alerte={alerte}
    >
      {etapes.map((etape) => (
        <LigneEtapeAValider
          key={etape.id}
          etape={etape}
          nomChantier={nomDuChantier(chantiers, etape.chantier_id)}
          maintenant={maintenant}
          enCours={enCours}
          reference={refLigne(etape.id)}
          onValider={(aValider) => {
            memoriser(aValider.id);
            onValider(aValider);
          }}
        />
      ))}
    </BlocAValider>
  );
}
