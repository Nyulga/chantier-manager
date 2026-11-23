// Page d'erreur : affichée à la place de l'application quand un écran plante au rendu.
import { Bouton } from '../Bouton/Bouton';
import { Pile } from '../Pile/Pile';
import { Texte } from '../Texte/Texte';
import { Titre } from '../Titre/Titre';

type PageErreurProps = {
  /** Recharge l'application : le seul moyen sûr de repartir d'un état cohérent après un plantage. */
  readonly onRecharger: () => void;
};

/**
 * Dit qu'une erreur est survenue, sans détail technique, et propose de recharger la page. Elle est
 * dans le design system parce que la barrière d'erreurs (`src/app`) l'affiche hors de toute
 * fonctionnalité, quand l'écran en cours est inutilisable.
 */
export function PageErreur({ onRecharger }: PageErreurProps) {
  return (
    <Pile>
      <Titre niveau={1}>Une erreur est survenue</Titre>
      <Texte>
        Quelque chose s&apos;est mal passé et la page ne peut pas s&apos;afficher. Recharge la page
        pour repartir : ton travail déjà enregistré n&apos;est pas perdu.
      </Texte>
      <Bouton onClick={onRecharger}>Recharger</Bouton>
    </Pile>
  );
}
