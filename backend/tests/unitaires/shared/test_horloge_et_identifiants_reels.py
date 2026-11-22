from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from app.shared.infrastructure.generateur_uuid7 import GenerateurUuid7
from app.shared.infrastructure.horloge_systeme import HorlogeSysteme

PARIS = ZoneInfo("Europe/Paris")
UUID_VERSION_7 = 7
VARIANTE_RFC = 0b10
HORODATAGE_MS = 1_700_000_000_123
NOMBRE_D_IDENTIFIANTS = 5000  # Plus que les 4096 valeurs du compteur d'une milliseconde.


def test_l_horloge_systeme_renvoie_un_instant_en_utc() -> None:
    avant = datetime.now(UTC)

    instant = HorlogeSysteme().maintenant()

    assert instant.utcoffset() == timedelta(0)
    assert avant <= instant <= datetime.now(UTC)


def test_la_date_du_jour_de_l_horloge_systeme_est_celle_de_paris() -> None:
    # Encadrer l'appel par deux lectures rend le test sûr même s'il passe minuit.
    avant = datetime.now(PARIS).date()

    aujourd_hui = HorlogeSysteme().aujourd_hui()

    assert avant <= aujourd_hui <= datetime.now(PARIS).date()


def test_un_identifiant_est_un_uuid_version_7_de_variante_rfc() -> None:
    identifiant = GenerateurUuid7().nouveau()

    assert identifiant.version == UUID_VERSION_7
    assert (identifiant.int >> 62) & 0b11 == VARIANTE_RFC


def test_un_identifiant_porte_la_date_de_sa_creation_en_millisecondes() -> None:
    generateur = GenerateurUuid7(horloge_ms=lambda: HORODATAGE_MS)

    identifiant = generateur.nouveau()

    assert identifiant.int >> 80 == HORODATAGE_MS


def test_les_identifiants_sont_uniques_et_strictement_croissants() -> None:
    generateur = GenerateurUuid7(horloge_ms=lambda: 1_700_000_000_000)

    identifiants = [generateur.nouveau() for _ in range(NOMBRE_D_IDENTIFIANTS)]

    assert identifiants == sorted(set(identifiants))


def test_un_retour_en_arriere_de_l_horloge_ne_casse_pas_l_ordre() -> None:
    instants = iter([1_700_000_000_500, 1_700_000_000_400])
    generateur = GenerateurUuid7(horloge_ms=lambda: next(instants))

    premier, second = generateur.nouveau(), generateur.nouveau()

    assert premier < second
