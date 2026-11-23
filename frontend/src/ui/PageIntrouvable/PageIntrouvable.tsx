// Page « introuvable » : affichée pour toute adresse inconnue, et pour un chantier que l'API ne connaît pas.
import { Lien } from '../Lien/Lien';
import { Pile } from '../Pile/Pile';
import { Texte } from '../Texte/Texte';
import { Titre } from '../Titre/Titre';

/**
 * Explique que la page n'existe pas et propose de revenir au tableau de bord. Elle est dans le
 * design system parce que plusieurs fonctionnalités l'affichent (une fonctionnalité ne peut pas
 * en importer une autre) : la route inconnue, et le détail d'un chantier introuvable.
 */
export function PageIntrouvable() {
  return (
    <Pile>
      <Titre niveau={1}>Page introuvable</Titre>
      <Texte>La page que tu cherches n&apos;existe pas ou a été déplacée.</Texte>
      <Lien vers="/">Retour au tableau de bord</Lien>
    </Pile>
  );
}
