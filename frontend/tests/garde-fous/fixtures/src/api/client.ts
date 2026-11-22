// Fixture conforme : faux client d'API, que seuls les services peuvent appeler.
export const client = {
  obtenirEtat: (): string => 'ok',
};
