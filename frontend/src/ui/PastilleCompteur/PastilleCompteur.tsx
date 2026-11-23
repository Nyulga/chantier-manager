// Composant `PastilleCompteur` du design system Balise : le nombre d'éléments qui attendent une action.

type PastilleCompteurProps = {
  readonly valeur: number;
  /** Vrai quand `valeur` est un minimum (liste coupée par l'API) : le « + » le dit en toutes lettres. */
  readonly auMoins?: boolean;
};

/**
 * Pastille jaune qui accompagne le titre du bloc « À valider ». Le jaune est réservé à ce qui
 * attend le chef (règle d'or) ; le nombre est écrit en chiffres, la couleur n'est pas le seul indice.
 * La valeur vient de l'API : la pastille ne compte rien.
 */
export function PastilleCompteur({ valeur, auMoins = false }: PastilleCompteurProps) {
  return (
    <span className="inline-flex h-7 min-w-7 items-center justify-center rounded-badge bg-accent px-2 text-secondaire font-extrabold tabular-nums text-on-accent">
      {auMoins ? `${String(valeur)}+` : valeur}
    </span>
  );
}
