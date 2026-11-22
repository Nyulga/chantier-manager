# Image de production de l'API : FastAPI servie par uvicorn, sans droits root.
# Construction à lancer depuis la racine du dépôt (voir compose.prod.yaml, `context: ..`).

# --- Étape 1 : installation des dépendances d'exécution avec uv --------------------------
FROM python:3.13-slim AS construction

# Version d'uv épinglée : une construction doit donner le même résultat d'un jour à l'autre.
COPY --from=ghcr.io/astral-sh/uv:0.13.9 /uv /usr/local/bin/uv

# Pas de téléchargement de Python (celui de l'image suffit) ; fichiers copiés plutôt que liés,
# pour que l'environnement virtuel reste utilisable une fois recopié dans l'image finale.
ENV UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1

WORKDIR /app

# Les dépendances sont installées avant le code : tant que `uv.lock` ne change pas,
# cette couche reste en cache. `--no-dev` écarte ruff, mypy, pytest et les autres outils.
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY backend/app ./app
# Les migrations sont appliquées au démarrage de l'API : Alembic les cherche à côté de `app/`.
COPY backend/alembic.ini ./alembic.ini
COPY backend/migrations ./migrations

# --- Étape 2 : image finale, minimale ------------------------------------------------------
FROM python:3.13-slim

# Utilisateur sans privilèges : une faille de l'API ne donne pas les droits root du conteneur.
RUN useradd --system --uid 10001 --no-create-home --shell /usr/sbin/nologin chantier \
    && mkdir /donnees \
    && chown chantier /donnees

WORKDIR /app
COPY --from=construction --chown=chantier /app /app

# La base SQLite vit dans le volume /donnees ; l'application lit CHANTIER_URL_BASE au
# démarrage (Parametres) et y applique les migrations.
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CHANTIER_URL_BASE=sqlite:////donnees/chantier.db

VOLUME /donnees
USER chantier
EXPOSE 8000

CMD ["uvicorn", "app.main:creer_application", "--factory", "--host", "0.0.0.0", "--port", "8000"]
