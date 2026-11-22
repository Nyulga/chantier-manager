// Composant racine : assemble les fournisseurs globaux et les routes.
import { Providers } from './providers';
import { RoutesApplication } from './routes';

/** Application complète, telle que montée par le point d'entrée `main.tsx`. */
export function App() {
  return (
    <Providers>
      <RoutesApplication />
    </Providers>
  );
}
