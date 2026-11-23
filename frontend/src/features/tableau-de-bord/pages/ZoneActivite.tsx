// Zone « Activité récente » du tableau de bord : lit le fil d'activité et le donne à sa section.
import { SectionActivite } from '../components/SectionActivite';
import { useActiviteRecente } from '../services/useActiviteRecente';
import type { ChantierDeListe } from '../services/useChantiers';

type ZoneActiviteProps = {
  readonly chantiers: readonly ChantierDeListe[] | undefined;
  /** Rôle de l'acteur, donné par l'API ; `undefined` tant qu'il n'est pas connu. */
  readonly role: Parameters<typeof SectionActivite>[0]['profil'];
  /** Erreur de lecture du rôle : elle remplace le fil, qui ne peut pas s'écrire sans lui. */
  readonly erreurRole: string | undefined;
  readonly maintenant: Date;
};

/** Le fil vient de l'API ; seul le rôle de l'acteur sert à écrire « Tu as… » plutôt que « Le chef a… ». */
export function ZoneActivite({ chantiers, role, erreurRole, maintenant }: ZoneActiviteProps) {
  const activite = useActiviteRecente();

  return (
    <SectionActivite
      entrees={activite.data}
      erreur={activite.error?.message ?? erreurRole}
      chantiers={chantiers}
      profil={role}
      maintenant={maintenant}
    />
  );
}
