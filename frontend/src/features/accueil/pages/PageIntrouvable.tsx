// Page 404 : affichée pour toute adresse qui ne correspond à aucune route.
import { Lien, Pile, Texte, Titre } from '@/ui';

/** Explique que la page n'existe pas et propose de revenir au tableau de bord. */
export function PageIntrouvable() {
  return (
    <Pile>
      <Titre niveau={1}>Page introuvable</Titre>
      <Texte>La page que tu cherches n’existe pas ou a été déplacée.</Texte>
      <Lien vers="/">Retour au tableau de bord</Lien>
    </Pile>
  );
}
