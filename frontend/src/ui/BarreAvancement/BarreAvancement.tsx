// Composant `BarreAvancement` du design system Balise : l'avancement d'un chantier.

type BarreAvancementProps = {
  readonly pourcentage: number;
  readonly etapesValidees?: number;
  readonly etapesTotal?: number;
  readonly libelle?: string;
};

const POURCENTAGE_MIN = 0;
const POURCENTAGE_MAX = 100;

/** En français, zéro et un prennent le singulier. */
function motEtapes(total: number): string {
  return total >= 2 ? 'étapes' : 'étape';
}

/**
 * Barre d'avancement : piste claire, remplissage `fg` (jamais `accent`, voir Balise §5),
 * toujours accompagnée d'un texte : « x / y étapes · z % », ou « z % » seul quand les nombres
 * d'étapes ne sont pas connus (la liste des chantiers ne reçoit de l'API que le pourcentage).
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
  const pourcentageTexte = `${String(Math.round(pourcentage))} %`;

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
        {etapesValidees === undefined || etapesTotal === undefined
          ? pourcentageTexte
          : `${String(etapesValidees)} / ${String(etapesTotal)} ${motEtapes(etapesTotal)} · ${pourcentageTexte}`}
      </p>
    </div>
  );
}
