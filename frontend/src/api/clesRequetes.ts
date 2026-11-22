// Clés TanStack Query des chantiers, de leurs étapes et du tableau de bord, partagées par les hooks de `services`.
// Elles sont hiérarchiques : invalider `chantier(id)` touche aussi `etapes(id)`, qui en dépend.

/** Clés des requêtes, une fonction par ressource. */
export const clesRequetes = {
  listeChantiers: () => ['chantiers', 'liste'] as const,
  // Le mot « detail » sépare les identifiants de chantier de la clé « liste » : un chantier dont
  // l'identifiant serait « liste » ne doit jamais partager la clé (et le cache) de la liste.
  chantier: (id: string) => ['chantiers', 'detail', id] as const,
  etapes: (chantierId: string) => [...clesRequetes.chantier(chantierId), 'etapes'] as const,
  // Les étapes à valider de tous les chantiers (réservées au chef) : la section « À valider ».
  etapesAValider: () => ['etapes', 'a-valider'] as const,
  // Préfixe du fil d'activité : le hook y ajoute la limite, et une invalidation couvre toutes les limites.
  activite: () => ['activite'] as const,
};
