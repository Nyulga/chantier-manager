// En-tête du tableau de bord : date du jour, titre, recherche (bientôt) et création d'un chantier.
import { ChampRecherche, EntetePage, formaterDateLongue, Icone, Lien } from '@/ui';

type EnTeteTableauDeBordProps = {
  /** Le jour affiché : transmis par la page, pour que le composant ne lise pas l'horloge. */
  readonly maintenant: Date;
  /** Le lien de création n'est proposé qu'au chef ; l'API reste seule juge (403 pour un ouvrier). */
  readonly peutCreerChantier: boolean;
};

/** Surtitre (date en toutes lettres), titre de la page et actions de l'en-tête. */
export function EnTeteTableauDeBord({ maintenant, peutCreerChantier }: EnTeteTableauDeBordProps) {
  return (
    <EntetePage surtitre={formaterDateLongue(maintenant)} titre="Tableau de bord">
      <ChampRecherche libelle="Rechercher un chantier" />
      {peutCreerChantier && (
        <Lien vers="/chantiers/nouveau" variante="principal">
          <Icone nom="plus" />
          Nouveau chantier
        </Lien>
      )}
    </EntetePage>
  );
}
