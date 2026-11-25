"""Garde des sous-agents : alignement de la table des droits sur les fiches d'agents et sur le hook.

Ces tests lisent les fichiers réels du dépôt : un agent ajouté ou renommé sans mise à jour de la
garde, ou un hook qui ne surveille plus les mêmes outils, fait échouer `just verifier`.
"""

import json
from pathlib import Path

import pytest

from tools.garde.droits import AGENTS_SANS_ECRITURE, DROITS_ECRITURE
from tools.garde.protocole import OUTILS_SURVEILLES

DEPOT = Path(__file__).resolve().parents[3]
FICHES = sorted((DEPOT / ".claude" / "agents").glob("*.md"))
OUTILS_D_ECRITURE = {"Write", "Edit"}


def lire_en_tete(fiche: Path) -> dict[str, str]:
    """Lit les champs `clé: valeur` de l'en-tête YAML d'une fiche d'agent."""
    en_tete = fiche.read_text(encoding="utf-8").split("---")[1]
    paires = (ligne.split(":", 1) for ligne in en_tete.splitlines() if ":" in ligne)
    return {cle.strip(): valeur.strip() for cle, valeur in paires}


def test_le_depot_contient_des_fiches_dagents() -> None:
    assert len(FICHES) >= len(DROITS_ECRITURE) + len(AGENTS_SANS_ECRITURE)


@pytest.mark.parametrize("fiche", FICHES, ids=lambda fiche: fiche.stem)
def test_chaque_agent_est_classe_selon_ses_outils_decriture(fiche: Path) -> None:
    en_tete = lire_en_tete(fiche)
    outils = {outil.strip() for outil in en_tete["tools"].split(",")}

    ecrit = bool(outils & OUTILS_D_ECRITURE)

    assert (en_tete["name"] in DROITS_ECRITURE) is ecrit
    assert (en_tete["name"] in AGENTS_SANS_ECRITURE) is not ecrit


def test_le_hook_du_projet_surveille_les_outils_de_la_garde_et_bloque_en_cas_de_panne() -> None:
    reglages = json.loads((DEPOT / ".claude" / "settings.json").read_text(encoding="utf-8"))

    (groupe,) = reglages["hooks"]["PreToolUse"]
    (hook,) = groupe["hooks"]

    assert set(groupe["matcher"].split("|")) == OUTILS_SURVEILLES
    assert "backend/tools/garde_agents.py" in hook["command"]
    assert hook["command"].endswith("|| exit 2")
