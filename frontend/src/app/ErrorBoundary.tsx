// Barrière d'erreurs de l'application : une erreur de rendu affiche une page d'erreur, jamais une page blanche.
import { Component, type ReactNode } from 'react';

import { PageErreur } from '@/ui';

type ErrorBoundaryProps = {
  readonly children: ReactNode;
  /** Recharge la page. Injectable pour les tests : jsdom ne sait pas recharger. */
  readonly rechargerPage?: () => void;
};

type ErrorBoundaryState = { readonly enErreur: boolean };

/** Recharge vraiment la page : seule voie sûre pour repartir d'un état que le plantage a pu corrompre. */
function recharger(): void {
  window.location.reload();
}

/**
 * React n'attrape les erreurs de rendu que dans une classe : c'est le seul composant de classe de
 * l'application. Les erreurs des requêtes n'arrivent pas ici (les écrans les affichent eux-mêmes) ;
 * seule une erreur de programmation ou une donnée inattendue qui fait planter un rendu déclenche
 * la page d'erreur. Elle ne montre aucun détail technique à l'utilisateur.
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  override state: ErrorBoundaryState = { enErreur: false };

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { enErreur: true };
  }

  override render() {
    if (this.state.enErreur) {
      return <PageErreur onRecharger={this.props.rechargerPage ?? recharger} />;
    }
    return this.props.children;
  }
}
