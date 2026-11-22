// Préparation commune des tests Vitest : matchers jest-dom, nettoyage du DOM après chaque test
// (Vitest n'expose pas `afterEach` en global ici) et origine des requêtes relatives.
import { cleanup } from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import { afterEach } from 'vitest';

/*
 * Dans un navigateur, `fetch('/api/…')` est résolu par rapport à l'adresse de la page. Le `fetch`
 * de Node, lui, refuse les adresses relatives faute d'origine. On lui donne l'origine de jsdom
 * à travers la clé globale que la bibliothèque undici (intégrée à Node) documente à cet effet,
 * pour que les tests se comportent comme le navigateur.
 */
// Les tests lancés en environnement Node (sans jsdom) n'ont ni fenêtre ni adresse de page.
if ('window' in globalThis) {
  Reflect.set(globalThis, Symbol.for('undici.globalOrigin.1'), new URL(window.location.href));
}

afterEach(() => {
  cleanup();
});
