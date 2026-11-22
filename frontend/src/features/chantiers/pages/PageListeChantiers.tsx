// Page « liste des chantiers » (adresse `/chantiers`) : une carte par chantier visible par l'acteur.
import { Alerte, EntetePage, Grille, Lien, Pile, Texte } from '@/ui';

import { ResumeChantier } from '../components/ResumeChantier';
import { useChantiers } from '../services/useChantiers';
import { useProfilCourant } from '../services/useProfilCourant';

/** Écran de la liste. Les chantiers affichés sont ceux que l'API renvoie pour le profil choisi. */
export function PageListeChantiers() {
  const chantiers = useChantiers();
  const profil = useProfilCourant();

  return (
    <Pile espace="grand">
      <EntetePage titre="Chantiers">
        {profil === 'chef' && (
          <Lien vers="/chantiers/nouveau" variante="principal">
            Nouveau chantier
          </Lien>
        )}
      </EntetePage>
      {chantiers.isPending && <Texte variante="secondaire">Chargement des chantiers…</Texte>}
      {chantiers.isError && <Alerte variante="erreur">{chantiers.error.message}</Alerte>}
      {chantiers.data?.length === 0 && <Texte>Aucun chantier pour le moment.</Texte>}
      {chantiers.data !== undefined && chantiers.data.length > 0 && (
        <Grille>
          {chantiers.data.map((chantier) => (
            <ResumeChantier key={chantier.id} chantier={chantier} niveauTitre={2} />
          ))}
        </Grille>
      )}
    </Pile>
  );
}
