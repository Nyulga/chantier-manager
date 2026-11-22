// Composant `CarteChantier` du design system Balise : le résumé d'un chantier, cliquable en entier.
import type { ReactNode } from 'react';
import { Link } from 'react-router';

import { BarreAvancement } from '../BarreAvancement/BarreAvancement';
import { Icone } from '../Icone/Icone';
import { Titre } from '../Titre/Titre';

type CarteChantierProps = {
  readonly nom: string;
  readonly vers: string;
  readonly adresse: string;
  /** Les puces d'état (`PuceChantier`) : « à valider », « en retard ». */
  readonly puces?: ReactNode;
  readonly etapesValidees: number;
  readonly etapesTotal: number;
  readonly pourcentage: number;
  /** Échéance déjà écrite (`JJ/MM/AAAA`). */
  readonly echeance: string;
  /** Délai déjà écrit (« J-54 », « En retard de 4 jours »). */
  readonly delai: string;
  readonly enRetard: boolean;
  /** Niveau du titre : 3 sous une section de page (par défaut), 2 quand la page n'a pas de section. */
  readonly niveauTitre?: 2 | 3 | undefined;
};

/**
 * Carte de chantier (Balise §5) : nom en titre condensé, puces d'état, adresse, avancement,
 * échéance et compte à rebours. Le délai est en `danger` quand l'API signale le retard, et
 * il est écrit en toutes lettres.
 *
 * Toute la carte est cliquable avec un seul lien : celui du titre, étiré sur la carte par un
 * pseudo-élément. Un lecteur d'écran n'entend ainsi que le nom du chantier, et le clavier ne
 * s'arrête qu'une fois. Le contour du focus est tracé autour de la carte entière.
 */
export function CarteChantier({
  nom,
  vers,
  adresse,
  puces,
  etapesValidees,
  etapesTotal,
  pourcentage,
  echeance,
  delai,
  enRetard,
  niveauTitre = 3,
}: CarteChantierProps) {
  return (
    <article className="relative flex h-full flex-col gap-4 rounded-controle border border-line bg-surface p-5 hover:border-fg has-focus-visible:outline-3 has-focus-visible:outline-offset-2 has-focus-visible:outline-fg">
      <div className="flex items-start justify-between gap-3">
        <Titre niveau={niveauTitre} taille={3}>
          <Link to={vers} className="after:absolute after:inset-0 focus-visible:outline-hidden">
            {nom}
          </Link>
        </Titre>
        {puces !== undefined && <div className="flex flex-wrap justify-end gap-2">{puces}</div>}
      </div>
      <p className="flex items-center gap-2 text-secondaire text-muted">
        <Icone nom="adresse" />
        {adresse}
      </p>
      <BarreAvancement
        libelle={`Avancement de ${nom}`}
        pourcentage={pourcentage}
        etapesValidees={etapesValidees}
        etapesTotal={etapesTotal}
      />
      <p className="mt-auto flex justify-between gap-3 border-t border-line-soft pt-3 text-secondaire">
        <span className="text-muted">
          Échéance <b className="font-bold tabular-nums text-fg">{echeance}</b>
        </span>
        <b className={`font-bold tabular-nums ${enRetard ? 'text-danger' : 'text-fg'}`}>{delai}</b>
      </p>
    </article>
  );
}
