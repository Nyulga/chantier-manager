"""Comportements propres à l'Unit of Work SQL : verrou optimiste et clés étrangères."""

from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

import pytest
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session, sessionmaker

from app.chantiers.infrastructure.sql.unit_of_work import SqlUnitOfWorkChantiers
from app.etapes.domain.cycle import ActionEtape
from app.etapes.infrastructure.sql.unit_of_work import SqlUnitOfWorkEtapes
from app.shared.application.erreurs import ServiceIndisponibleError
from app.shared.domain.acteur import Acteur, Role
from app.shared.domain.erreurs import ConflitVersionError
from app.shared.infrastructure.sql.moteur import creer_moteur, creer_usine_sessions
from tests.conftest import url_sqlite
from tests.fabriques.chantiers import un_chantier
from tests.fabriques.etapes import ID_CHANTIER, une_etape

OUVRIER = Acteur(Role.OUVRIER)
INSTANT = datetime(2026, 11, 22, 9, 0, tzinfo=UTC)
VERSION_APRES_UNE_TRANSITION = 2
CHANTIER_INCONNU = UUID(int=404)


def preparer_une_etape(usine: sessionmaker[Session]) -> SqlUnitOfWorkEtapes:
    with SqlUnitOfWorkChantiers(usine) as chantiers:
        chantiers.chantiers.ajouter(un_chantier(ID_CHANTIER.int))
        chantiers.valider()
    uow = SqlUnitOfWorkEtapes(usine)
    with uow:
        uow.etapes.ajouter(une_etape())
        uow.valider()
    return uow


def test_une_modification_sur_un_objet_lu_avant_celle_d_un_autre_donne_un_conflit_de_version(
    usine_sessions: sessionmaker[Session],
) -> None:
    uow = preparer_une_etape(usine_sessions)
    premiere, seconde = SqlUnitOfWorkEtapes(usine_sessions), SqlUnitOfWorkEtapes(usine_sessions)
    identifiant = une_etape().id

    # Les transactions commencent par `BEGIN IMMEDIATE` : deux transactions ne se chevauchent
    # plus, la seconde attendrait la fin de la première. Le conflit reste possible quand
    # l'objet a été lu dans une transaction déjà terminée (ici validée à vide), puis modifié
    # après qu'un autre a enregistré la sienne : c'est ce que le numéro de version détecte.
    with seconde:
        lue_trop_tot = seconde.etapes.obtenir(identifiant)
        seconde.valider()
        with premiere:
            premiere.etapes.obtenir(identifiant).appliquer(ActionEtape.DEMARRER, OUVRIER, INSTANT)
            premiere.valider()
        lue_trop_tot.appliquer(ActionEtape.DEMARRER, OUVRIER, INSTANT)
        with pytest.raises(ConflitVersionError):
            seconde.valider()
    with uow:
        relue = uow.etapes.obtenir(identifiant)

    # La transition perdante n'a rien laissé : ni version en plus, ni entrée d'historique.
    assert (relue.version, len(relue.historique)) == (VERSION_APRES_UNE_TRANSITION, 1)


def test_la_base_refuse_une_etape_dont_le_chantier_n_existe_pas(
    usine_sessions: sessionmaker[Session],
) -> None:
    uow = SqlUnitOfWorkEtapes(usine_sessions)

    with uow, pytest.raises(IntegrityError):
        uow.etapes.ajouter(une_etape())
        uow.valider()


def test_un_uow_est_reutilisable_apres_une_erreur(usine_sessions: sessionmaker[Session]) -> None:
    uow = preparer_une_etape(usine_sessions)

    # Un chantier inconnu : la clé étrangère est refusée, ce qui n'est pas un conflit entre
    # deux utilisateurs et remonte donc telle quelle.
    with uow, pytest.raises(IntegrityError):
        uow.etapes.ajouter(une_etape(chantier_id=CHANTIER_INCONNU))
        uow.valider()
    with uow:
        etapes = uow.etapes.lister_par_chantiers([ID_CHANTIER])

    assert len(etapes) == 1


def test_deux_ajouts_simultanes_au_meme_ordre_donnent_un_conflit_sans_ecraser_le_premier(
    usine_sessions: sessionmaker[Session],
) -> None:
    uow = preparer_une_etape(usine_sessions)
    premiere, seconde = SqlUnitOfWorkEtapes(usine_sessions), SqlUnitOfWorkEtapes(usine_sessions)
    gagnante = une_etape(ordre=2)
    perdante = replace(gagnante, id=UUID(int=999))

    # Deux ajouts qui ont lu les mêmes étapes calculent le même ordre suivant.
    with premiere, seconde:
        premiere.etapes.ajouter(gagnante)
        seconde.etapes.ajouter(perdante)
        premiere.valider()
        with pytest.raises(ConflitVersionError):
            seconde.valider()
    with uow:
        etapes = uow.etapes.lister_par_chantiers([ID_CHANTIER])

    assert [etape.id for etape in etapes] == [une_etape().id, gagnante.id]


def test_une_base_inaccessible_devient_un_service_indisponible(tmp_path: Path) -> None:
    # Le dossier de la base n'existe pas : SQLite ne peut pas ouvrir le fichier.
    moteur = creer_moteur(url_sqlite(tmp_path / "absent"))
    uow = SqlUnitOfWorkChantiers(creer_usine_sessions(moteur))

    with pytest.raises(ServiceIndisponibleError) as erreur, uow:
        uow.chantiers.lister()

    assert "SELECT" not in str(erreur.value)
    moteur.dispose()


def test_une_table_absente_remonte_telle_quelle_au_lieu_d_un_service_indisponible(
    tmp_path: Path,
) -> None:
    # Le fichier existe mais son schéma est vide : c'est un défaut du programme ou du
    # déploiement, que le 503 « réessaie dans un instant » masquerait à tort.
    moteur = creer_moteur(url_sqlite(tmp_path))
    uow = SqlUnitOfWorkChantiers(creer_usine_sessions(moteur))

    with pytest.raises(OperationalError, match="no such table"), uow:
        uow.chantiers.lister()

    moteur.dispose()
