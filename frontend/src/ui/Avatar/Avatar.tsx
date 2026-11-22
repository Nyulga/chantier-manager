// Composant `Avatar` du design system Balise : les initiales d'une personne dans un cercle.

type AvatarProps = {
  readonly initiales: string;
};

/**
 * Cercle d'initiales (rayon à 50 %, Balise §4). Il est décoratif : le nom de la personne est
 * toujours écrit à côté, on le cache donc des lecteurs d'écran pour ne pas le lire deux fois.
 */
export function Avatar({ initiales }: AvatarProps) {
  return (
    <span
      aria-hidden="true"
      className="inline-flex size-8 shrink-0 items-center justify-center rounded-avatar bg-bg text-etiquette font-bold"
    >
      {initiales}
    </span>
  );
}
