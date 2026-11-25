// Composant `ChampPiege` du design system Balise : un champ de saisie que seuls les robots remplissent.

type ChampPiegeProps = {
  readonly valeur: string;
  readonly onChange: (valeur: string) => void;
};

/**
 * Champ « piège » (`site_web`) d'un formulaire d'écriture. Un humain ne le voit pas, ne peut pas
 * y arriver au clavier et ne l'entend pas : il reste donc toujours vide. Un robot qui remplit
 * tous les champs du DOM le remplit, et l'API bloque alors son adresse en écriture.
 *
 * Il n'est volontairement pas masqué par `display: none` ni `hidden` : beaucoup de robots
 * ignorent les champs ainsi cachés. Il est seulement retiré de l'affichage (`sr-only`, qui le
 * réduit à un point sans le sortir de la page), puis retiré de tout ce qui sert à une personne :
 * - `aria-hidden` : les lecteurs d'écran l'ignorent ;
 * - `tabIndex={-1}` : il n'est pas dans l'ordre de tabulation, sans quoi un élément masqué aux
 *   lecteurs d'écran mais atteignable au clavier serait un défaut d'accessibilité (WCAG 4.1.2) ;
 * - `autoComplete="off"` : le navigateur ne le remplit pas à la place d'un humain, ce qui
 *   bloquerait à tort une personne réelle.
 * Il n'a pas de libellé : il n'est jamais annoncé, et son nom (`site_web`) suffit à un robot.
 */
export function ChampPiege({ valeur, onChange }: ChampPiegeProps) {
  return (
    <div aria-hidden="true" className="sr-only">
      <input
        type="text"
        name="site_web"
        value={valeur}
        tabIndex={-1}
        autoComplete="off"
        onChange={(evenement) => {
          onChange(evenement.target.value);
        }}
      />
    </div>
  );
}
