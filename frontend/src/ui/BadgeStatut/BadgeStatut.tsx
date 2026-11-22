// Composant `BadgeStatut` du design system Balise : le statut d'une étape, en toutes lettres.

/** Statuts d'une étape, tels que l'API les renvoie. */
export type StatutEtape = 'a_faire' | 'en_cours' | 'terminee_a_valider' | 'validee';

type BadgeStatutProps = {
  readonly statut: StatutEtape;
};

/** Libellé français et couleurs de chaque statut (Balise §2.3, tokens `statut-*` du thème). */
const PRESENTATION_PAR_STATUT: Record<StatutEtape, { libelle: string; classes: string }> = {
  a_faire: {
    libelle: 'À faire',
    classes: 'bg-statut-a-faire-fond text-statut-a-faire-texte',
  },
  en_cours: {
    libelle: 'En cours',
    classes: 'bg-statut-en-cours-fond text-statut-en-cours-texte',
  },
  terminee_a_valider: {
    libelle: 'Terminée (à valider)',
    classes: 'bg-statut-a-valider-fond text-statut-a-valider-texte',
  },
  validee: {
    libelle: 'Validée',
    classes: 'bg-statut-validee-fond text-statut-validee-texte',
  },
};

/**
 * Badge de statut. Le libellé est écrit en toutes lettres : la couleur n'est jamais le seul indice.
 *
 * « Terminée (à valider) » attend une action du chef : seul statut à porter le jaune haute
 * visibilité et les rayures « balise » (règle d'or du design system). Les rayures forment un
 * repère décoratif à côté du texte, car posées dessous elles le rendraient illisible.
 */
export function BadgeStatut({ statut }: BadgeStatutProps) {
  const { libelle, classes } = PRESENTATION_PAR_STATUT[statut];

  return (
    <span
      className={`inline-flex items-center gap-2 rounded-badge px-2 py-1 text-badge font-bold ${classes}`}
    >
      {statut === 'terminee_a_valider' && (
        <span aria-hidden="true" className="rayures-balise h-4 w-rayure rounded-badge" />
      )}
      {libelle}
    </span>
  );
}
