// Composant `ChampRecherche` du design system Balise : un champ de recherche pas encore disponible.
import { MentionBientot } from '../MentionBientot/MentionBientot';

type ChampRechercheProps = {
  readonly libelle: string;
};

/**
 * Champ de recherche désactivé, avec la mention « Bientôt » (décision du propriétaire du produit :
 * la recherche viendra plus tard). Le champ est nommé par `aria-label` : une loupe et une mention
 * suffisent à le comprendre, un libellé visible de plus alourdirait l'en-tête sur mobile.
 */
export function ChampRecherche({ libelle }: ChampRechercheProps) {
  return (
    <div className="flex w-full items-center gap-2 tablette:w-auto tablette:shrink-0">
      <input
        type="search"
        disabled
        aria-label={libelle}
        placeholder={libelle}
        className="min-h-cible-mobile min-w-0 flex-1 rounded-controle border border-line bg-surface px-3 text-texte text-muted tablette:w-champ-recherche tablette:flex-none ordinateur:min-h-cible"
      />
      <span className="shrink-0 text-muted">
        <MentionBientot />
      </span>
    </div>
  );
}
