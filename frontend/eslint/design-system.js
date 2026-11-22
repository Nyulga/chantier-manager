// Blocs ESLint du design system Balise (règle 05) : hors de `src/ui`, on n'écrit ni HTML
// interactif ou stylé, ni `className`, ni `style` ; et nulle part on n'écrit une valeur
// Tailwind arbitraire (`bg-[#F2A900]`, `p-[13px]`) : seuls les tokens du thème existent.

const POUR_CONSOMMER = 'Utilise un composant de src/ui (ajoute-le au design system s’il manque).';

/** Éléments HTML réservés aux composants de `src/ui`. */
const ELEMENTS_INTERDITS = ['button', 'input', 'select', 'textarea', 'a', 'img', 'table'].map(
  (element) => ({ element, message: `<${element}> est réservé à src/ui. ${POUR_CONSOMMER}` }),
);

/** Props de style réservées à `src/ui`. */
const PROPS_INTERDITES = ['className', 'style'].map((propName) => ({
  propName,
  message: `La prop ${propName} est réservée à src/ui. ${POUR_CONSOMMER}`,
}));

/*
 * Valeurs arbitraires de Tailwind, dans n'importe quelle chaîne ou gabarit de texte :
 * - `bg-[#F2A900]`, `md:p-[13px]` : utilitaire avec valeur entre crochets ;
 * - `[&_p]:mt-2`, `[color:red]` : variante ou propriété arbitraire.
 */
const VALEUR_ARBITRAIRE = String.raw`(^|[\s:!])-?[a-z][a-z0-9-]*-\[[^\]]+\]`;
const VARIANTE_ARBITRAIRE = String.raw`(^|[\s:!])\[[^\]\s]*[:&][^\]\s]*\]`;
const MESSAGE_ARBITRAIRE =
  'Valeur Tailwind arbitraire interdite : utilise un token du thème (src/ui/theme/balise.css).';

const SELECTEURS_ARBITRAIRES = [VALEUR_ARBITRAIRE, VARIANTE_ARBITRAIRE].flatMap((motif) => [
  { selector: `Literal[value=/${motif}/]`, message: MESSAGE_ARBITRAIRE },
  { selector: `TemplateElement[value.raw=/${motif}/]`, message: MESSAGE_ARBITRAIRE },
]);

export function blocDesignSystem() {
  return [
    {
      files: ['src/**/*.{ts,tsx}'],
      ignores: ['src/ui/**'],
      rules: {
        'react/forbid-elements': ['error', { forbid: ELEMENTS_INTERDITS }],
        'react/forbid-dom-props': ['error', { forbid: PROPS_INTERDITES }],
        'react/forbid-component-props': ['error', { forbid: PROPS_INTERDITES }],
      },
    },
    {
      files: ['src/**/*.{ts,tsx}'],
      rules: { 'no-restricted-syntax': ['error', ...SELECTEURS_ARBITRAIRES] },
    },
  ];
}
