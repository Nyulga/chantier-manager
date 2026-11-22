// Classes des boutons Balise, partagées par `Bouton` et par `Lien` quand un lien a l'allure d'un bouton.

/**
 * Variantes de Balise (§5) :
 * - `principal` : l'action à mener (jaune sur mobile, graphite sur ordinateur) ;
 * - `secondaire` : une action annexe ;
 * - `danger` : un refus ou une action destructrice.
 */
export type VarianteBouton = 'principal' | 'secondaire' | 'danger';

const BASE =
  'inline-flex w-full items-center justify-center gap-2 rounded-controle px-5 font-bold ' +
  'tablette:w-auto disabled:opacity-50';

const CLASSES_PAR_VARIANTE: Record<VarianteBouton, string> = {
  // Jaune réservé au bouton principal mobile (règle d'or de Balise) ; graphite dès l'ordinateur.
  principal:
    'min-h-cible-mobile-confort bg-accent text-on-accent ' +
    'ordinateur:min-h-cible ordinateur:bg-fg ordinateur:text-surface',
  secondaire: 'min-h-cible-mobile border border-line bg-surface text-fg ordinateur:min-h-cible',
  danger:
    'min-h-cible-mobile border-2 border-danger bg-transparent text-danger ordinateur:min-h-cible',
};

/** Classes complètes d'un bouton de la variante demandée. */
export function classesBouton(variante: VarianteBouton): string {
  return `${BASE} ${CLASSES_PAR_VARIANTE[variante]}`;
}
