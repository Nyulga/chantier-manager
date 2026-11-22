// Tests de la traduction des erreurs de l'API en erreurs JavaScript au message affichable.
import { expect, it } from 'vitest';

import { erreurApi, MESSAGE_ERREUR_PAR_DEFAUT } from './erreurApi';

it('reprend le détail en français d’une réponse problem+json', () => {
  const erreur = erreurApi({ status: 422, detail: 'Le commentaire du refus est obligatoire.' });

  expect(erreur).toBeInstanceOf(Error);
  expect(erreur.message).toBe('Le commentaire du refus est obligatoire.');
});

it('utilise un message par défaut quand la réponse n’a pas de détail', () => {
  expect(erreurApi(undefined).message).toBe(MESSAGE_ERREUR_PAR_DEFAUT);
  expect(erreurApi({ status: 500 }).message).toBe(MESSAGE_ERREUR_PAR_DEFAUT);
});

it('ignore un détail qui n’est pas un texte', () => {
  expect(erreurApi({ detail: [{ msg: 'invalid' }] }).message).toBe(MESSAGE_ERREUR_PAR_DEFAUT);
});
