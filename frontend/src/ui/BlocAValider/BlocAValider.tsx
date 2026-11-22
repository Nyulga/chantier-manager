// Composant `BlocAValider` du design system Balise : le bloc des étapes qui attendent la décision du chef.
import { useId, type ReactNode, type Ref } from 'react';

import { BandeauRayures } from '../BandeauRayures/BandeauRayures';
import { PastilleCompteur } from '../PastilleCompteur/PastilleCompteur';
import { Titre } from '../Titre/Titre';

type BlocAValiderProps = {
  readonly titre: string;
  /** Nombre d'étapes à valider, tel que l'API le donne. */
  readonly compteur: number;
  readonly sousTitre: string;
  /** Rend le titre focalisable par programme : voir `Titre`. */
  readonly refTitre?: Ref<HTMLHeadingElement>;
  /** Message au niveau du bloc, hors des lignes (l'erreur d'une validation par exemple). */
  readonly alerte?: ReactNode;
  /** Les lignes (`LigneAValider`). */
  readonly children: ReactNode;
};

/**
 * Bloc surligné par le bandeau rayé « balise », la pastille jaune et la liste des étapes.
 *
 * C'est l'endroit par excellence où le jaune et les rayures s'appliquent (règle d'or de
 * Balise : tout ce qui attend une action du chef). Quand il n'y a rien à valider, la page
 * n'affiche pas ce bloc : un bandeau jaune sans action à mener contredirait la règle.
 */
export function BlocAValider({
  titre,
  compteur,
  sousTitre,
  refTitre,
  alerte,
  children,
}: BlocAValiderProps) {
  const identifiantTitre = useId();

  return (
    <section
      aria-labelledby={identifiantTitre}
      className="overflow-hidden rounded-controle border border-line bg-surface"
    >
      <BandeauRayures />
      <div className="flex flex-wrap items-center justify-between gap-3 px-5 pt-5 pb-2">
        <div className="flex items-center gap-3">
          <div id={identifiantTitre}>
            <Titre niveau={2} refTitre={refTitre}>
              {titre}
            </Titre>
          </div>
          <PastilleCompteur valeur={compteur} />
        </div>
        <p className="text-secondaire text-muted">{sousTitre}</p>
      </div>
      {alerte !== undefined && <div className="px-5 pb-3">{alerte}</div>}
      <ul className="flex flex-col">{children}</ul>
    </section>
  );
}
