// Hook de création d'un chantier : envoie la saisie à l'API et rafraîchit la liste.
import { useMutation, useQueryClient } from '@tanstack/react-query';

import { creerClientApi } from '@/api/client';
import { clesRequetes } from '@/api/clesRequetes';
import { donneesOuErreur } from '@/api/erreurApi';

/**
 * Saisie du formulaire de création, à plat (un champ de formulaire par propriété).
 *
 * Les dates sont au format ISO (`AAAA-MM-JJ`) et le budget reste un texte : il part tel quel à
 * l'API, qui le lit comme un décimal exact. Le frontend ne le convertit jamais en nombre.
 */
export type SaisieChantier = {
  readonly nom: string;
  readonly voie: string;
  readonly codePostal: string;
  readonly ville: string;
  readonly client: string;
  readonly dateDebut: string;
  readonly echeance: string;
  readonly budget: string;
  /** Champ piège : un humain ne le voit pas, donc il reste vide (voir `ChampPiege`). */
  readonly siteWeb: string;
};

/** Type de l'erreur que lève la création, pour les formulaires qui affichent ses erreurs par champ. */
export type { ErreurApi } from '@/api/erreurApi';

/**
 * Crée un chantier. Le hook met la saisie à la forme de l'API (adresse imbriquée, champs en
 * `snake_case`), pour que les composants ne connaissent pas le format du contrat.
 */
export function useCreerChantier() {
  const clientRequetes = useQueryClient();

  return useMutation({
    mutationFn: async (saisie: SaisieChantier) =>
      donneesOuErreur(
        await creerClientApi().POST('/chantiers', {
          body: {
            nom: saisie.nom,
            adresse: { voie: saisie.voie, code_postal: saisie.codePostal, ville: saisie.ville },
            client: saisie.client,
            date_debut: saisie.dateDebut,
            echeance: saisie.echeance,
            budget: saisie.budget,
            // Le champ piège part seulement s'il est rempli, pour que l'API repère le robot.
            ...(saisie.siteWeb !== '' && { site_web: saisie.siteWeb }),
          },
        }),
      ),
    onSuccess: async () => {
      await clientRequetes.invalidateQueries({ queryKey: clesRequetes.listeChantiers() });
    },
  });
}
