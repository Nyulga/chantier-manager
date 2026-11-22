// Violation volontaire : un appel à window.fetch en dehors de src/api (contournement de l'interdit).
export async function appelFetchFenetre(): Promise<number> {
  const reponse = await window.fetch('/api/health');

  return reponse.status;
}
