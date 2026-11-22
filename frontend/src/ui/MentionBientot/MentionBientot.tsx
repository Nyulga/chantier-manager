// Composant `MentionBientot` du design system Balise : la mention d'une fonction pas encore disponible.

/**
 * Étiquette « Bientôt » : elle accompagne un élément désactivé (recherche, équipe, invitation).
 * Elle est écrite en toutes lettres : la couleur, ou le seul état désactivé, ne suffit pas à
 * expliquer pourquoi l'élément ne répond pas.
 */
export function MentionBientot() {
  return (
    <span className="rounded-badge border border-current px-2 py-1 text-etiquette font-semibold uppercase">
      Bientôt
    </span>
  );
}
