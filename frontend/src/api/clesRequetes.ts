// Clés TanStack Query des chantiers, de leurs étapes et du tableau de bord, partagées par les hooks de `services`.
// Elles sont hiérarchiques : invalider `chantier(id)` touche aussi `etapes(id)`, qui en dépend.

/** Clés des requêtes, une fonction par ressource. */
export const clesRequetes = {
  listeChantiers: () => ['chantiers', 'liste'] as const,
  // Le mot « detail » sépare les identifiants de chantier de la clé « liste » : un chantier dont
  // l'identifiant serait « liste » ne doit jamais partager la clé (et le cache) de la liste.
  chantier: (id: string) => ['chantiers', 'detail', id] as const,
  etapes: (chantierId: string) => [...clesRequetes.chantier(chantierId), 'etapes'] as const,
  // Les étapes à valider de tous les chantiers : la section « À valider ».
  etapesAValider: () => ['etapes', 'a-valider'] as const,
  // Les capacités de l'acteur portent le profil : sans lui, les droits du chef resteraient en cache
  // (et s'afficheraient un instant) après le passage à ouvrier.
  capacites: (profil: string) => ['moi', profil] as const,
  // Le fil d'activité du tableau de bord.
  activite: () => ['activite'] as const,
};
