// Zone « À valider » du tableau de bord : lit les étapes à valider et branche leur validation.
import { SectionAValider } from '../components/SectionAValider';
import type { ChantierDeListe } from '../services/useChantiers';
import { useEtapesAValider } from '../services/useEtapesAValider';
import { useValiderEtape } from '../services/useValiderEtape';

type ZoneAValiderProps = {
  /** Vrai si l'API annonce le droit de lister les étapes à valider (`/api/moi`). */
  readonly autorisee: boolean;
  readonly chantiers: readonly ChantierDeListe[] | undefined;
  readonly maintenant: Date;
};

/**
 * Sans le droit, la zone n'affiche rien et la requête ne part pas : un ouvrier ne voit jamais la
 * section, pas même un instant « Chargement… » avant qu'un refus ne la masque.
 */
export function ZoneAValider({ autorisee, chantiers, maintenant }: ZoneAValiderProps) {
  const aValider = useEtapesAValider(autorisee);
  const validation = useValiderEtape();

  if (!autorisee) {
    return null;
  }
  return (
    <SectionAValider
      etapes={aValider.data?.etapes}
      tronquee={aValider.data?.tronquee === true}
      erreurChargement={aValider.error?.message}
      chantiers={chantiers}
      maintenant={maintenant}
      enCours={validation.isPending}
      erreurValidation={
        validation.isError
          ? { titre: validation.variables.titre, message: validation.error.message }
          : undefined
      }
      onValider={(etape) => {
        validation.mutate(etape);
      }}
    />
  );
}
