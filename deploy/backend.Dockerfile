# Image de production de l'API : FastAPI servie par uvicorn, sans droits root.
# Construction à lancer depuis la racine du dépôt (voir compose.prod.yaml, `context: ..`).
#
# Les images de base sont épinglées par empreinte (digest), le tag restant en commentaire :
# une construction ne change pas parce qu'un tag a été déplacé. Dependabot propose les mises
# à jour de ces empreintes (voir .github/dependabot.yml).

# --- Étape 1 : installation des dépendances d'exécution avec uv --------------------------
# python:3.13-slim
FROM python@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90 AS construction

# Version d'uv épinglée : une construction doit donner le même résultat d'un jour à l'autre.
# ghcr.io/astral-sh/uv:0.13.9
COPY --from=ghcr.io/astral-sh/uv@sha256:d3b601f0c7b118bc1753febf7c41cc80981df678445e0254284eecf84db79a7d /uv /usr/local/bin/uv

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
# python:3.13-slim
FROM python@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d350d98134cf1070bc106ee9ed90

# Utilisateur sans privilèges : une faille de l'API ne donne pas les droits root du conteneur.
# Seul /donnees lui appartient : c'est le seul endroit où il peut écrire.
RUN useradd --system --uid 10001 --no-create-home --shell /usr/sbin/nologin chantier \
    && mkdir /donnees \
    && chown chantier /donnees

WORKDIR /app
# Le code reste la propriété de root (pas de `--chown`) : l'utilisateur 10001 le lit sans pouvoir
# le modifier, même si le système de fichiers du conteneur n'était pas en lecture seule.
COPY --from=construction /app /app

# La base SQLite vit dans le volume /donnees ; l'application lit CHANTIER_URL_BASE au
# démarrage (Parametres) et y applique les migrations. Le système de fichiers étant en
# lecture seule en production, Python ne doit écrire aucun fichier `.pyc` (le bytecode est
# déjà compilé à la construction, grâce à UV_COMPILE_BYTECODE).
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CHANTIER_URL_BASE=sqlite:////donnees/chantier.db

VOLUME /donnees
USER chantier
EXPOSE 8000

CMD ["uvicorn", "app.main:creer_application", "--factory", "--host", "0.0.0.0", "--port", "8000"]
