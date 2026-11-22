// Composant `BarreAvancement` du design system Balise : l'avancement d'un chantier.

type BarreAvancementProps = {
  readonly pourcentage: number;
  readonly etapesValidees: number;
  readonly etapesTotal: number;
  readonly libelle?: string;
};

const POURCENTAGE_MIN = 0;
const POURCENTAGE_MAX = 100;

/**
 * Barre d'avancement : piste claire, remplissage `fg` (jamais `accent`, voir Balise §5),
 * toujours accompagnée du texte « x / y étapes · z % ».
 *
 * Le pourcentage et les compteurs viennent de l'API : le composant ne calcule rien, il arrondit
 * seulement pour l'affichage. La largeur est bornée à [0, 100] pour qu'une valeur aberrante
 * ne fasse pas déborder la barre.
 */
export function BarreAvancement({
  pourcentage,
  etapesValidees,
  etapesTotal,
  libelle = 'Avancement',
}: BarreAvancementProps) {
  const largeur = Math.min(POURCENTAGE_MAX, Math.max(POURCENTAGE_MIN, pourcentage));
  // En français, zéro et un prennent le singulier.
  const mot = etapesTotal >= 2 ? 'étapes' : 'étape';

  return (
    <div className="flex flex-col gap-1">
      <div
        role="progressbar"
        aria-label={libelle}
        aria-valuenow={pourcentage}
        aria-valuemin={POURCENTAGE_MIN}
        aria-valuemax={POURCENTAGE_MAX}
        className="h-barre w-full overflow-hidden rounded-controle bg-statut-a-faire-fond"
      >
        <div className="h-full bg-fg" style={{ width: `${String(largeur)}%` }} />
      </div>
      <p className="text-secondaire tabular-nums text-muted">
        {`${String(etapesValidees)} / ${String(etapesTotal)} ${mot} · ${String(Math.round(pourcentage))} %`}
      </p>
    </div>
  );
}
