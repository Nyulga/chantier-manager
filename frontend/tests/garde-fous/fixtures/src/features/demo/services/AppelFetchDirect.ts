// Violation volontaire : un appel à fetch en dehors de src/api.
export async function appelFetchDirect(): Promise<number> {
  const reponse = await fetch('/api/health');

  return reponse.status;
}
