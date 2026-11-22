// Violation volontaire : un import de Radix en dehors de src/ui.
import * as Dialog from '@radix-ui/react-dialog';

export function PageRadix() {
  return <Dialog.Root />;
}
