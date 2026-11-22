// Clés TanStack Query des chantiers et de leurs étapes, partagées par les hooks de `services`.
// Elles sont hiérarchiques : invalider `['chantiers', id]` touche aussi les étapes de ce chantier.

/** Clés des requêtes, une fonction par ressource. */
export const clesRequetes = {
  listeChantiers: () => ['chantiers', 'liste'] as const,
  chantier: (id: string) => ['chantiers', id] as const,
  etapes: (chantierId: string) => ['chantiers', chantierId, 'etapes'] as const,
};
