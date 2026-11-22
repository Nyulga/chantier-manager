"""Création de l'application FastAPI : seul point d'entrée du backend.

C'est la composition root. Elle crée l'application, y enregistre les routeurs et la
traduction des erreurs, et branche les implémentations sur les ports ; elle ne
contient aucune logique métier (règle 06).
"""

from fastapi import FastAPI

from app.chantiers.api.routes import creer_routeur as creer_routeur_chantiers
from app.composition.base_de_donnees import BaseDeDonnees
from app.composition.chantiers import FournisseursChantiers
from app.composition.etapes import FournisseursEtapes
from app.composition.parametres import Parametres
from app.etapes.api.routes import creer_routeur as creer_routeur_etapes
from app.shared.api import sante
from app.shared.api.erreurs import enregistrer_gestionnaires_erreurs
from app.shared.infrastructure.generateur_uuid7 import GenerateurUuid7


def creer_application(parametres: Parametres | None = None) -> FastAPI:
    """Crée l'application FastAPI.

    Toute l'API vit sous `/api` : le frontend et l'API sont servis sur le même
    domaine, ce qui évite d'ouvrir le CORS (intent.md, §2.1). Le schéma OpenAPI,
    dont est généré le client TypeScript, est donc lui aussi sous `/api`.

    Les migrations de la base sont appliquées au démarrage (cycle de vie) ; créer
    l'application, par exemple pour exporter le schéma OpenAPI, ne touche pas la base.

    Args:
        parametres: configuration à utiliser ; lue de l'environnement si elle est omise.
    """
    parametres = parametres or Parametres()
    base = BaseDeDonnees(parametres.url_base)
    # Un seul générateur pour tout le processus : c'est lui qui garantit l'ordre des UUID v7.
    generateur_id = GenerateurUuid7()
    application = FastAPI(
        title="chantier-manager",
        openapi_url="/api/openapi.json",
        docs_url="/api/docs",
        redoc_url=None,
        lifespan=base.cycle_de_vie,
    )
    enregistrer_gestionnaires_erreurs(application)
    application.include_router(sante.routeur, prefix="/api")
    application.include_router(
        creer_routeur_chantiers(FournisseursChantiers(base.usine_sessions, generateur_id)),
        prefix="/api",
    )
    application.include_router(
        creer_routeur_etapes(FournisseursEtapes(base.usine_sessions, generateur_id)),
        prefix="/api",
    )
    return application
