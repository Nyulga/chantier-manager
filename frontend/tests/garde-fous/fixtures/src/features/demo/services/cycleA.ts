// Violation volontaire : cycleA et cycleB s'importent mutuellement (import circulaire).
import { depuisB } from './cycleB';

export function depuisA(profondeur: number): string {
  return profondeur > 0 ? depuisB(profondeur - 1) : 'fin';
}
