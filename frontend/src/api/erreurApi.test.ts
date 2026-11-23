// Tests de la traduction des erreurs de l'API en erreurs JavaScript au message affichable.
import { expect, it } from 'vitest';

import { donneesOuErreur, ErreurApi, erreurApi, MESSAGE_ERREUR_PAR_DEFAUT } from './erreurApi';

it("reprend le détail en français d'une réponse problem+json", () => {
  const erreur = erreurApi({ status: 422, detail: 'Le commentaire du refus est obligatoire.' });

  expect(erreur).toBeInstanceOf(ErreurApi);
  expect(erreur.message).toBe('Le commentaire du refus est obligatoire.');
});

it("utilise un message par défaut quand la réponse n'a pas de détail", () => {
  expect(erreurApi(undefined).message).toBe(MESSAGE_ERREUR_PAR_DEFAUT);
  expect(erreurApi({ status: 500 }).message).toBe(MESSAGE_ERREUR_PAR_DEFAUT);
});

it("ignore un détail qui n'est pas un texte", () => {
  expect(erreurApi({ detail: [{ msg: 'invalid' }] }).message).toBe(MESSAGE_ERREUR_PAR_DEFAUT);
});

it('garde le statut HTTP de la réponse', () => {
  expect(erreurApi({ detail: 'Introuvable.' }, 404).statut).toBe(404);
  expect(erreurApi({ detail: 'Introuvable.' }).statut).toBeUndefined();
});

it("expose les erreurs par champ d'une réponse 422", () => {
  const erreur = erreurApi(
    {
      detail: 'Les données envoyées sont invalides.',
      erreurs: [
        { champ: 'adresse.code_postal', message: 'Le code postal est trop long.' },
        { champ: 'nom', message: 'Le nom est obligatoire.' },
      ],
    },
    422,
  );

  expect(erreur.erreurs).toEqual([
    { champ: 'adresse.code_postal', message: 'Le code postal est trop long.' },
    { champ: 'nom', message: 'Le nom est obligatoire.' },
  ]);
});

it("n'expose aucune erreur par champ quand la réponse n'en donne pas ou les donne mal formées", () => {
  expect(erreurApi({ detail: 'Conflit.' }, 409).erreurs).toEqual([]);
  expect(erreurApi({ detail: 'x', erreurs: 'nom' }).erreurs).toEqual([]);
  expect(
    erreurApi({ detail: 'x', erreurs: [{ champ: 'nom' }, null, { champ: 'a', message: 'ok' }] })
      .erreurs,
  ).toEqual([{ champ: 'a', message: 'ok' }]);
});

it('se reconnaît comme introuvable pour un statut 404, et pour lui seul', () => {
  expect(erreurApi({ detail: 'Introuvable.' }, 404).introuvable).toBe(true);
  expect(erreurApi({ detail: 'Refusé.' }, 403).introuvable).toBe(false);
  expect(erreurApi({ detail: 'Panne.' }).introuvable).toBe(false);
});

it("donneesOuErreur renvoie les données d'une réponse réussie", () => {
  const resultat = { data: [1, 2], response: new Response() };

  expect(donneesOuErreur(resultat)).toEqual([1, 2]);
});

it("donneesOuErreur lève l'erreur de l'API, avec son statut et ses champs", () => {
  const resultat = {
    error: { detail: 'Invalide.', erreurs: [{ champ: 'titre', message: 'Trop long.' }] },
    response: new Response(null, { status: 422 }),
  };

  expect(() => donneesOuErreur(resultat)).toThrow(ErreurApi);
  try {
    donneesOuErreur(resultat);
  } catch (erreur) {
    expect(erreur).toMatchObject({
      statut: 422,
      erreurs: [{ champ: 'titre', message: 'Trop long.' }],
    });
  }
});

const ERREUR_422 = erreurApi(
  {
    detail: 'Les données envoyées sont invalides.',
    erreurs: [
      { champ: 'adresse.code_postal', message: 'Le code postal est trop long.' },
      { champ: 'echeance', message: "L'échéance précède le début." },
      { champ: 'echeance', message: 'Autre message sur le même champ.' },
    ],
  },
  422,
);

it("donne le message d'un champ, le premier quand il y en a plusieurs", () => {
  expect(ERREUR_422.messageDuChamp('adresse.code_postal')).toBe('Le code postal est trop long.');
  expect(ERREUR_422.messageDuChamp('echeance')).toBe("L'échéance précède le début.");
  expect(ERREUR_422.messageDuChamp('nom')).toBeUndefined();
});

it("garde pour l'alerte globale les messages des champs que le formulaire n'affiche pas", () => {
  expect(ERREUR_422.messageGlobal(['adresse.code_postal'])).toBe(
    "L'échéance précède le début. Autre message sur le même champ.",
  );
});

it("n'a rien à dire dans l'alerte globale quand chaque message a son champ", () => {
  expect(ERREUR_422.messageGlobal(['adresse.code_postal', 'echeance'])).toBeUndefined();
});

it("garde le détail dans l'alerte globale quand l'erreur ne désigne aucun champ", () => {
  const conflit = erreurApi({ detail: 'Cette étape a déjà changé de statut.' }, 409);

  expect(conflit.messageGlobal(['titre'])).toBe('Cette étape a déjà changé de statut.');
});

it("envoie dans l'alerte globale une erreur sans champ (clé inattendue à la racine du corps)", () => {
  const inattendue = erreurApi(
    {
      detail: 'Requête invalide.',
      erreurs: [
        { champ: '', message: "Ce champ n'est pas attendu." },
        { champ: 'nom', message: 'Le nom est requis.' },
      ],
    },
    422,
  );

  expect(inattendue.messageGlobal(['nom'])).toBe("Ce champ n'est pas attendu.");
  expect(inattendue.messageDuChamp('nom')).toBe('Le nom est requis.');
});
