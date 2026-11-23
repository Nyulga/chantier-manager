// Lecture de l'identifiant du chantier affiché, partagée par les hooks de plusieurs fonctionnalités.

/**
 * Valide le paramètre `id` d'une route `/chantiers/:id`. Les routes qui l'utilisent le déclarent
 * toujours : son absence est une erreur de programmation, qui doit se voir (la barrière d'erreurs
 * l'affiche) plutôt que d'envoyer à l'API une requête avec un identifiant vide.
 *
 * Lève :
 *     Error : la route n'a pas de paramètre `id`.
 */
export function lireIdentifiantChantier(id: string | undefined): string {
  if (id === undefined) {
    throw new Error("La route n'a pas d'identifiant de chantier.");
  }
  return id;
}
