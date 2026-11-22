// Formatage des dates pour l'affichage : JJ/MM/AAAA, le format français (Balise §6).

const DATE_ISO = /^(\d{4})-(\d{2})-(\d{2})$/;

/**
 * Écrit une date ISO (`2026-09-30`, telle que l'API la renvoie) au format `30/09/2026`.
 *
 * On réordonne le texte plutôt que de passer par `Date` : une `Date` convertit en heure locale
 * et peut décaler la journée selon le fuseau. Un texte qui n'est pas une date ISO est rendu tel quel.
 */
export function formaterDate(dateIso: string): string {
  const morceaux = DATE_ISO.exec(dateIso);
  if (morceaux === null) {
    return dateIso;
  }
  const [, annee, mois, jour] = morceaux;
  return `${String(jour)}/${String(mois)}/${String(annee)}`;
}
