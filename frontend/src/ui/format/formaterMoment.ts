// Formatage d'un moment (date et heure) : « hier à 17:42 », ou « le 20/11/2026 à 17:42 ».
import { formaterDate } from './formaterDate';

const MILLISECONDES_PAR_JOUR = 24 * 60 * 60 * 1000;

/** Nombre écrit sur deux chiffres, « 08 ». */
function deuxChiffres(nombre: number): string {
  return String(nombre).padStart(2, '0');
}

/** Heure locale sur deux chiffres, « 08:05 ». */
function formaterHeure(date: Date): string {
  return `${deuxChiffres(date.getHours())}:${deuxChiffres(date.getMinutes())}`;
}

/** Début de la journée locale : sert à compter des jours civils, pas des tranches de 24 heures. */
function debutDeJournee(date: Date): number {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate()).getTime();
}

/** Date locale au format `JJ/MM/AAAA`, sans passer par l'UTC qui pourrait décaler la journée. */
function dateLocale(date: Date): string {
  const iso = `${String(date.getFullYear())}-${deuxChiffres(date.getMonth() + 1)}-${deuxChiffres(date.getDate())}`;
  return formaterDate(iso);
}

/**
 * Écrit un moment renvoyé par l'API (ISO avec fuseau) à l'heure de l'utilisateur : « aujourd'hui »
 * et « hier » restent relatifs, le reste est une date complète. `maintenant` est un paramètre
 * pour que le résultat ne dépende pas de l'horloge (tests, et affichage stable).
 */
export function formaterMoment(momentIso: string, maintenant: Date): string {
  const moment = new Date(momentIso);
  if (Number.isNaN(moment.getTime())) {
    return momentIso;
  }
  const heure = formaterHeure(moment);
  const joursEcoules = Math.round(
    (debutDeJournee(maintenant) - debutDeJournee(moment)) / MILLISECONDES_PAR_JOUR,
  );
  if (joursEcoules === 0) {
    return `aujourd’hui à ${heure}`;
  }
  return joursEcoules === 1 ? `hier à ${heure}` : `le ${dateLocale(moment)} à ${heure}`;
}
