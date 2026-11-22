// Point d'entrée du navigateur : charge le thème Balise et monte l'application dans `#root`.
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import '@/ui/theme/balise.css';

import { App } from './App';

const elementRacine = document.getElementById('root');

// Mieux vaut échouer tout de suite, avec un message clair, qu'afficher une page blanche.
if (elementRacine === null) {
  throw new Error("L'élément #root est introuvable : vérifie le fichier index.html.");
}

createRoot(elementRacine).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
