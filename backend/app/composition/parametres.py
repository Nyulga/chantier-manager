"""Paramètres de l'application, lus une seule fois (règle 06)."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.shared.application.limites_debit import ECRITURES_PAR_FENETRE, LECTURES_PAR_FENETRE

# Taille maximale du corps d'une requête : les requêtes de l'API sont de petits JSON.
# C'est la même valeur que le `request_body` de Caddy (`deploy/Caddyfile.extrait`) : le
# serveur applique le plafond en amont, l'application le refait pour ne pas dépendre
# de lui (défense en profondeur).
TAILLE_MAX_CORPS = 64 * 1024


class Parametres(BaseSettings):
    """Configuration issue des variables d'environnement `CHANTIER_*`.

    Les valeurs par défaut sont sûres pour la production, sauf la base : une base
    SQLite dans le dossier courant, qui convient au développement local. En production,
    `CHANTIER_URL_BASE` pointe vers le volume. Seule la composition root lit cette
    configuration, puis la transmet en paramètre.
    """

    model_config = SettingsConfigDict(env_prefix="CHANTIER_")

    url_base: str = "sqlite:///./chantier.db"

    # La documentation interactive et `openapi.json` donnent la carte complète de l'API
    # à qui l'attaque : ils sont fermés par défaut. La génération du client TypeScript
    # (`just client`) et les tests l'ouvrent explicitement.
    documentation_exposee: bool = False

    # Noms d'hôte que l'API accepte dans l'en-tête `Host` (sans le port), pour refuser
    # les requêtes qui n'arrivent pas par le site. Par défaut, uniquement la machine
    # locale (développement, test de bout en bout, sonde de santé du conteneur). En
    # démo comme en production, `CHANTIER_HOTES_ACCEPTES` ajoute le nom public, en
    # JSON : `["chantier-ultra.ddns.net", "127.0.0.1"]` (garder `127.0.0.1` pour la
    # sonde de santé).
    hotes_acceptes: list[str] = ["localhost", "127.0.0.1"]

    taille_max_corps: int = TAILLE_MAX_CORPS

    # Seuils de la limite de débit, par adresse et par minute. Les valeurs par défaut sont
    # les décisions du propriétaire (`limites_debit.py`) : la production ne les change pas.
    # Ils ne sont réglables que pour les tests et le test de bout en bout, qui écrivent
    # bien plus de 20 fois par minute depuis une seule adresse. Un seuil nul couperait toute
    # l'API : il est refusé au démarrage.
    ecritures_par_minute: int = Field(default=ECRITURES_PAR_FENETRE, ge=1)
    lectures_par_minute: int = Field(default=LECTURES_PAR_FENETRE, ge=1)
