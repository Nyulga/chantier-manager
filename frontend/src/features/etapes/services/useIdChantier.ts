// Hook de l'identifiant du chantier affiché, lu dans l'adresse de la page (`/chantiers/:id`).
import { useParams } from 'react-router';

/**
 * Renvoie l'identifiant du chantier de l'adresse. Les routes qui l'utilisent le déclarent
 * toujours : son absence est une erreur de programmation, qui doit se voir (la barrière d'erreurs
 * l'affiche) plutôt que d'envoyer à l'API une requête avec un identifiant vide.
 *
 * Lève :
 *     Error : la route n'a pas de paramètre `id`.
 */
export function useIdChantier(): string {
  const { id } = useParams();
  if (id === undefined) {
    throw new Error("La route n'a pas d'identifiant de chantier.");
  }
  return id;
}
