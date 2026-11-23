// Tests du profil courant : lecture et écriture dans localStorage, avec repli sur « chef ».
import { afterEach, expect, it, vi } from 'vitest';

import { CLE_PROFIL, ecouterProfil, enregistrerProfil, lireProfil } from './profil';

afterEach(() => {
  localStorage.clear();
  vi.restoreAllMocks();
});

it("renvoie « chef » quand aucun profil n'est enregistré", () => {
  expect(lireProfil()).toBe('chef');
});

it('renvoie le profil enregistré', () => {
  enregistrerProfil('ouvrier');

  expect(lireProfil()).toBe('ouvrier');
  expect(localStorage.getItem(CLE_PROFIL)).toBe('ouvrier');
});

it("ignore une valeur enregistrée qui n'est pas un profil connu", () => {
  localStorage.setItem(CLE_PROFIL, 'administrateur');

  expect(lireProfil()).toBe('chef');
});

it('renvoie « chef » quand localStorage est inaccessible en lecture', () => {
  vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
    throw new Error('accès refusé');
  });

  expect(lireProfil()).toBe('chef');
});

it('ne plante pas quand localStorage est inaccessible en écriture', () => {
  vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
    throw new Error('quota dépassé');
  });

  expect(() => {
    enregistrerProfil('ouvrier');
  }).not.toThrow();
});

it("prévient les écouteurs quand le profil change, jusqu'à leur désinscription", () => {
  const rappel = vi.fn();
  const arreter = ecouterProfil(rappel);

  enregistrerProfil('ouvrier');
  arreter();
  enregistrerProfil('chef');

  expect(rappel).toHaveBeenCalledOnce();
});

it('prévient aussi les écouteurs quand un autre onglet modifie le profil', () => {
  const rappel = vi.fn();
  const arreter = ecouterProfil(rappel);

  window.dispatchEvent(new StorageEvent('storage', { key: CLE_PROFIL }));
  arreter();

  expect(rappel).toHaveBeenCalledOnce();
});
