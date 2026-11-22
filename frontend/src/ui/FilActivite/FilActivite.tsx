// Composant `FilActivite` du design system Balise : la liste des derniers événements.
import { Avatar } from '../Avatar/Avatar';

/** Un événement du fil : tout est déjà écrit, le composant ne fait que le mettre en page. */
export type EntreeFil = {
  readonly id: string;
  readonly initiales: string;
  readonly qui: string;
  readonly quoi: string;
  /** Précision sous la phrase, par exemple « chantier · hier à 17:42 ». */
  readonly contexte: string;
};

type FilActiviteProps = {
  /** Nom de la liste, lu par les lecteurs d'écran. */
  readonly libelle: string;
  readonly entrees: readonly EntreeFil[];
};

/**
 * Liste ordonnée (du plus récent au plus ancien, ordre de l'API) : un avatar, la phrase
 * « qui + quoi » puis le contexte en texte secondaire, sur fond `surface`.
 */
export function FilActivite({ libelle, entrees }: FilActiviteProps) {
  return (
    <ol
      aria-label={libelle}
      className="flex flex-col rounded-controle border border-line bg-surface px-5 py-1"
    >
      {entrees.map((entree) => (
        <li key={entree.id} className="flex gap-3 border-t border-line-soft py-4 first:border-t-0">
          <Avatar initiales={entree.initiales} />
          <div className="flex min-w-0 flex-col gap-1">
            <p className="text-secondaire">
              <strong className="font-semibold">{entree.qui}</strong> {entree.quoi}
            </p>
            <p className="text-etiquette text-muted">{entree.contexte}</p>
          </div>
        </li>
      ))}
    </ol>
  );
}
