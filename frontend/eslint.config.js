// Configuration ESLint du frontend. Toute la logique est dans `eslint/` : ce fichier se contente
// de l'appliquer à la racine du projet, pour que les tests des garde-fous puissent aussi
// l'appliquer à un mini-projet de fixtures.
import { creerConfig } from './eslint/creer-config.js';

export default creerConfig({ racine: import.meta.dirname });
