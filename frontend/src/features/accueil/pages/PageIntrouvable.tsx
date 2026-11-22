// Page 404 : affichée pour toute adresse qui ne correspond à aucune route.
import { Lien, Pile, Texte, Titre } from '@/ui';

/** Explique que la page n'existe pas et propose de revenir à la liste des chantiers. */
export function PageIntrouvable() {
  return (
    <Pile>
      <Titre niveau={2}>Page introuvable</Titre>
      <Texte>La page que tu cherches n’existe pas ou a été déplacée.</Texte>
      <Lien vers="/">Retour aux chantiers</Lien>
    </Pile>
  );
}
