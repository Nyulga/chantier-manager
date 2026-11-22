"""Création de l'application FastAPI : seul point d'entrée du backend.

C'est la composition root. Elle crée l'application et y enregistre les routeurs ;
elle ne contient aucune logique métier (règle 06).
"""

from fastapi import FastAPI

from app.shared.api import sante


def creer_application() -> FastAPI:
    """Crée l'application FastAPI.

    Toute l'API vit sous `/api` : le frontend et l'API sont servis sur le même
    domaine, ce qui évite d'ouvrir le CORS (intent.md, §2.1). Le schéma OpenAPI,
    dont est généré le client TypeScript, est donc lui aussi sous `/api`.
    """
    application = FastAPI(
        title="chantier-manager",
        openapi_url="/api/openapi.json",
        docs_url="/api/docs",
        redoc_url=None,
    )
    application.include_router(sante.routeur, prefix="/api")
    return application
