// Erreur d'API d'exemple pour les tests des composants, qui la reçoivent par leurs props.
import { ErreurApi } from '@/api/erreurApi';

/** Une erreur de l'API, comme celle d'un hook : `erreurs` liste les champs en cause (422). */
export function erreurApiDeTest(
  message: string,
  erreurs: readonly { champ: string; message: string }[] = [],
): ErreurApi {
  return new ErreurApi(message, undefined, erreurs);
}
