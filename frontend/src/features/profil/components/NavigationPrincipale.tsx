// Entrées de la navigation principale : tableau de bord, chantiers, et les fonctions à venir.
import { ElementNavigation, ElementNavigationBientot } from '@/ui';

type NavigationPrincipaleProps = {
  /** Compteur de « Mes chantiers » ; absent tant que la liste n'est pas chargée. */
  readonly nombreChantiers?: number | undefined;
};

/**
 * « Équipe » et « Inviter un utilisateur » sont affichés désactivés avec la mention « Bientôt » :
 * décision du propriétaire du produit, ces fonctions ne sont pas encore livrées.
 */
export function NavigationPrincipale({ nombreChantiers }: NavigationPrincipaleProps) {
  return (
    <>
      <ElementNavigation vers="/" exact icone="tableau-de-bord">
        Tableau de bord
      </ElementNavigation>
      <ElementNavigation vers="/chantiers" icone="chantiers" compteur={nombreChantiers}>
        Mes chantiers
      </ElementNavigation>
      <ElementNavigationBientot icone="equipe">Équipe</ElementNavigationBientot>
      <ElementNavigationBientot icone="invitation">Inviter un utilisateur</ElementNavigationBientot>
    </>
  );
}
