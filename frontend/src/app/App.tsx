// Composant racine : assemble les fournisseurs globaux et les routes.
import { ErrorBoundary } from './ErrorBoundary';
import { Providers } from './providers';
import { RoutesApplication } from './routes';

/**
 * Application complète, telle que montée par le point d'entrée `main.tsx`. La barrière d'erreurs
 * entoure les routes, et reste dans les fournisseurs : sa page d'erreur n'a besoin de rien d'autre.
 */
export function App() {
  return (
    <Providers>
      <ErrorBoundary>
        <RoutesApplication />
      </ErrorBoundary>
    </Providers>
  );
}
