// Clés TanStack Query des chantiers et de leurs étapes, partagées par les hooks de `services`.
// Elles sont hiérarchiques : invalider `chantier(id)` touche aussi `etapes(id)`, qui en dépend.

/** Clés des requêtes, une fonction par ressource. */
export const clesRequetes = {
  listeChantiers: () => ['chantiers', 'liste'] as const,
  // Le mot « detail » sépare les identifiants de chantier de la clé « liste » : un chantier dont
  // l'identifiant serait « liste » ne doit jamais partager la clé (et le cache) de la liste.
  chantier: (id: string) => ['chantiers', 'detail', id] as const,
  etapes: (chantierId: string) => [...clesRequetes.chantier(chantierId), 'etapes'] as const,
};
