// Violation volontaire : cycleB importe cycleA, qui importe cycleB (import circulaire).
import { depuisA } from './cycleA';

export function depuisB(profondeur: number): string {
  return depuisA(profondeur);
}
