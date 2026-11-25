"""Petite application FastAPI pour tester un middleware seul, sans base de données.

L'application réelle ne branche les protections qu'à l'étape de composition : un test
de middleware construit donc la sienne, avec une route factice qui note ses appels,
pour prouver qu'un refus se fait « sans appeler la route ».
"""

from fastapi import APIRouter, FastAPI, Request

from app.shared.api.erreurs import enregistrer_gestionnaires_erreurs

METHODES_DE_LA_RESSOURCE = ["GET", "HEAD", "POST", "PUT", "PATCH", "DELETE"]


def une_petite_application() -> tuple[FastAPI, list[str]]:
    """Crée l'application, avec `/api/ressource`, `/api/health` et `/hors-api`.

    Renvoie aussi la liste où chaque appel de route note sa méthode et son chemin.
    """
    appels: list[str] = []
    application = FastAPI()
    enregistrer_gestionnaires_erreurs(application)
    routeur = APIRouter(prefix="/api")

    @routeur.api_route("/ressource", methods=METHODES_DE_LA_RESSOURCE)
    async def ressource(requete: Request) -> dict[str, int]:
        appels.append(f"{requete.method} {requete.url.path}")
        corps = await requete.body()
        return {"octets": len(corps)}

    @routeur.get("/health")
    def sante() -> dict[str, str]:
        appels.append("GET /api/health")
        return {"statut": "ok"}

    @routeur.get("/erreur")
    def erreur() -> None:
        raise RuntimeError

    application.include_router(routeur)

    @application.get("/hors-api")
    def hors_api() -> dict[str, str]:
        appels.append("GET /hors-api")
        return {"statut": "ok"}

    return application, appels
