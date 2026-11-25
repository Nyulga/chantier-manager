"""Migration 0003 : purge des caractères désormais refusés dans les adresses déjà enregistrées.

Lire un chantier reconstruit son adresse par le constructeur de l'objet valeur : une adresse
enregistrée avant le lot S8, avec un caractère devenu interdit, ferait échouer sa lecture et
celle de toute la liste (500 sur la page d'accueil). La migration les nettoie avant que
l'application ne les relise.
"""

from pathlib import Path
from uuid import UUID

import pytest
from alembic import command
from sqlalchemy import Engine, text

from app.chantiers.domain.adresse import Adresse
from app.chantiers.infrastructure.sql.unit_of_work import SqlUnitOfWorkChantiers
from app.composition.base_de_donnees import configuration_alembic
from app.shared.domain.erreurs import ValeurInvalideError
from app.shared.infrastructure.sql.moteur import creer_moteur, creer_usine_sessions
from tests.conftest import url_sqlite

CHANTIER_A_NETTOYER = UUID(int=1)
CHANTIER_NORMAL = UUID(int=2)
VOIE_NORMALE = "12 rue des Lilas"
CODE_POSTAL_NORMAL = "69001"
VILLE_NORMALE = "Lyon"
VALEUR_NEUTRE = "À préciser"
# Les caractères sont construits par leur numéro : écrits tels quels, ils seraient invisibles ici.
SAUT_DE_LIGNE = chr(0x0A)
SEPARATEUR_DE_LIGNE = chr(0x2028)
USAGE_PRIVE = chr(0xE000)
ESPACE_SANS_CHASSE = chr(0x200B)
LIANT_SANS_CHASSE = chr(0x200D)
ACCENT_AIGU_COMBINANT = chr(0x0301)
FAMILLE = f"\U0001f468{LIANT_SANS_CHASSE}\U0001f469{LIANT_SANS_CHASSE}\U0001f467"

COLONNES = ["voie", "code_postal", "ville"]
NORMALES = {"voie": VOIE_NORMALE, "code_postal": CODE_POSTAL_NORMAL, "ville": VILLE_NORMALE}
# (texte enregistré, texte attendu après la migration). Ils tiennent en 10 caractères,
# la longueur maximale du code postal, pour servir aux trois parties de l'adresse.
CAS_A_NETTOYER = [
    pytest.param("ab" + SEPARATEUR_DE_LIGNE + "cd", "ab cd", id="u2028"),
    pytest.param("ab" + USAGE_PRIVE + "cd", "abcd", id="usage-prive"),
    pytest.param("ab" + ESPACE_SANS_CHASSE + "cd", "abcd", id="u200b"),
    pytest.param("ab" + SAUT_DE_LIGNE + "cd", "ab cd", id="saut-de-ligne"),
    pytest.param(SEPARATEUR_DE_LIGNE + "ab", "ab", id="espace-creee-en-debut"),
    pytest.param(ESPACE_SANS_CHASSE * 2, VALEUR_NEUTRE, id="que-des-invisibles"),
    pytest.param(LIANT_SANS_CHASSE, VALEUR_NEUTRE, id="que-des-liants"),
    pytest.param("  " + ESPACE_SANS_CHASSE, VALEUR_NEUTRE, id="espaces-et-invisibles"),
]


def inserer_un_chantier(moteur: Engine, identifiant: UUID, adresse: dict[str, str]) -> None:
    """Enregistre un chantier directement en SQL, comme le faisait la version précédente."""
    requete = text(
        "INSERT INTO chantiers VALUES (:id, 'Chantier', :voie, :code_postal, :ville, "
        "'Client', '2026-01-01', '2026-06-01', 1000)"
    )
    with moteur.begin() as connexion:
        connexion.execute(requete, {"id": identifiant.hex, **adresse})


def lire_l_adresse(moteur: Engine, identifiant: UUID) -> Adresse:
    """Relit l'adresse par le repository, c'est-à-dire par le constructeur de l'objet valeur."""
    with SqlUnitOfWorkChantiers(creer_usine_sessions(moteur)) as uow:
        return uow.chantiers.obtenir(identifiant).adresse


def lire_le_texte_brut(moteur: Engine, identifiant: UUID) -> dict[str, str]:
    requete = text("SELECT voie, code_postal, ville FROM chantiers WHERE id = :id")
    with moteur.connect() as connexion:
        ligne = connexion.execute(requete, {"id": identifiant.hex}).one()
    return {"voie": ligne.voie, "code_postal": ligne.code_postal, "ville": ligne.ville}


def une_base_a_la_revision_0002(tmp_path: Path) -> tuple[Engine, str]:
    url = url_sqlite(tmp_path)
    command.upgrade(configuration_alembic(url), "0002")
    return creer_moteur(url), url


@pytest.mark.parametrize("colonne", COLONNES)
def test_avant_la_migration_une_adresse_refusee_fait_echouer_la_lecture(
    tmp_path: Path, colonne: str
) -> None:
    moteur, _ = une_base_a_la_revision_0002(tmp_path)
    inserer_un_chantier(
        moteur, CHANTIER_A_NETTOYER, {**NORMALES, colonne: "ab" + ESPACE_SANS_CHASSE}
    )

    with pytest.raises(ValeurInvalideError):
        lire_l_adresse(moteur, CHANTIER_A_NETTOYER)
    moteur.dispose()


@pytest.mark.parametrize("colonne", COLONNES)
@pytest.mark.parametrize(("enregistre", "attendu"), CAS_A_NETTOYER)
def test_la_migration_nettoie_chaque_partie_de_l_adresse(
    tmp_path: Path, colonne: str, enregistre: str, attendu: str
) -> None:
    moteur, url = une_base_a_la_revision_0002(tmp_path)
    inserer_un_chantier(moteur, CHANTIER_A_NETTOYER, {**NORMALES, colonne: enregistre})

    command.upgrade(configuration_alembic(url), "0003")

    adresse = lire_l_adresse(moteur, CHANTIER_A_NETTOYER)
    assert getattr(adresse, colonne) == attendu
    autres = [autre for autre in COLONNES if autre != colonne]
    assert [getattr(adresse, autre) for autre in autres] == [NORMALES[autre] for autre in autres]
    moteur.dispose()


def test_la_liste_des_chantiers_se_relit_apres_la_migration(tmp_path: Path) -> None:
    moteur, url = une_base_a_la_revision_0002(tmp_path)
    inserer_un_chantier(
        moteur, CHANTIER_A_NETTOYER, {**NORMALES, "voie": "12 ru" + ESPACE_SANS_CHASSE + "e"}
    )
    inserer_un_chantier(moteur, CHANTIER_NORMAL, NORMALES)

    command.upgrade(configuration_alembic(url), "0003")

    with SqlUnitOfWorkChantiers(creer_usine_sessions(moteur)) as uow:
        identifiants = [chantier.id for chantier in uow.chantiers.lister()]
    assert identifiants == [CHANTIER_A_NETTOYER, CHANTIER_NORMAL]
    moteur.dispose()


def test_une_adresse_normale_n_est_pas_modifiee(tmp_path: Path) -> None:
    moteur, url = une_base_a_la_revision_0002(tmp_path)
    # Accents, apostrophe, marques combinantes, drapeau et emoji composé d'un liant : tout cela
    # reste admis, la migration n'y touche pas.
    adresse = {
        "voie": f"3 bis, rue de l'Église {FAMILLE} e{ACCENT_AIGU_COMBINANT}tage",
        "code_postal": "2A004",
        "ville": "Saint-Étienne-du-Rouvray \U0001f3f4\U000e0067\U000e0062\U000e007f",
    }
    inserer_un_chantier(moteur, CHANTIER_NORMAL, adresse)

    command.upgrade(configuration_alembic(url), "0003")

    assert lire_le_texte_brut(moteur, CHANTIER_NORMAL) == adresse
    assert lire_l_adresse(moteur, CHANTIER_NORMAL) == Adresse(**adresse)
    moteur.dispose()


def test_un_nom_refuse_enregistre_avant_le_lot_se_relit_sans_erreur(tmp_path: Path) -> None:
    # Seule l'adresse est un objet valeur reconstruit à la lecture : le nom, le client et les
    # titres sont recopiés tels quels, sans repasser par les contrôles. C'est pourquoi la
    # migration se limite aux colonnes de l'adresse.
    moteur, url = une_base_a_la_revision_0002(tmp_path)
    requete = text(
        "INSERT INTO chantiers VALUES (:id, :nom, 'Rue', '69001', 'Lyon', "
        "'Client', '2026-01-01', '2026-06-01', 1000)"
    )
    with moteur.begin() as connexion:
        connexion.execute(requete, {"id": CHANTIER_NORMAL.hex, "nom": "Ecole" + ESPACE_SANS_CHASSE})

    command.upgrade(configuration_alembic(url), "0003")

    with SqlUnitOfWorkChantiers(creer_usine_sessions(moteur)) as uow:
        assert uow.chantiers.obtenir(CHANTIER_NORMAL).nom == "Ecole" + ESPACE_SANS_CHASSE
    moteur.dispose()


def test_le_retour_a_0002_garde_les_donnees_nettoyees(tmp_path: Path) -> None:
    # La purge est irréversible : les caractères retirés ne peuvent pas être rétablis.
    moteur, url = une_base_a_la_revision_0002(tmp_path)
    inserer_un_chantier(
        moteur, CHANTIER_A_NETTOYER, {**NORMALES, "voie": "12 ru" + ESPACE_SANS_CHASSE + "e"}
    )
    configuration = configuration_alembic(url)
    command.upgrade(configuration, "0003")

    command.downgrade(configuration, "0002")

    assert lire_le_texte_brut(moteur, CHANTIER_A_NETTOYER)["voie"] == "12 rue"
    moteur.dispose()


def test_la_migration_0003_est_rejouable(tmp_path: Path) -> None:
    moteur, url = une_base_a_la_revision_0002(tmp_path)
    inserer_un_chantier(
        moteur, CHANTIER_A_NETTOYER, {**NORMALES, "ville": ESPACE_SANS_CHASSE + "Lyon"}
    )
    configuration = configuration_alembic(url)
    command.upgrade(configuration, "0003")
    command.downgrade(configuration, "0002")

    command.upgrade(configuration, "0003")

    assert lire_l_adresse(moteur, CHANTIER_A_NETTOYER).ville == "Lyon"
    moteur.dispose()
