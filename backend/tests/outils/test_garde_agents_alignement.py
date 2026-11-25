"""Garde des sous-agents : alignement de la table des droits sur les fiches d'agents et sur le hook.

Ces tests lisent les fichiers réels du dépôt : un agent ajouté ou renommé sans mise à jour de la
garde, ou un hook qui ne surveille plus les mêmes outils, fait échouer `just verifier`.
"""

import json
from pathlib import Path

from tools.garde.agents import AGENTS_SANS_ECRITURE, VERIFICATEURS
from tools.garde.droits import DROITS_ECRITURE
from tools.garde.protocole import OUTILS_SURVEILLES

DEPOT = Path(__file__).resolve().parents[3]
FICHES = sorted((DEPOT / ".claude" / "agents").glob("*.md"))
OUTILS_D_ECRITURE = {"Write", "Edit"}


def lire_en_tete(fiche: Path) -> dict[str, str]:
    """Lit les champs `clé: valeur` de l'en-tête YAML d'une fiche d'agent."""
    en_tete = fiche.read_text(encoding="utf-8").split("---")[1]
    paires = (ligne.split(":", 1) for ligne in en_tete.splitlines() if ":" in ligne)
    return {cle.strip(): valeur.strip() for cle, valeur in paires}


def ecrit(fiche: Path) -> bool:
    """Dit si l'agent a un outil d'écriture ; une fiche sans `tools` hérite de tous les outils."""
    en_tete = lire_en_tete(fiche)
    if "tools" not in en_tete:
        return True
    return bool({outil.strip() for outil in en_tete["tools"].split(",")} & OUTILS_D_ECRITURE)


def test_les_agents_qui_ecrivent_sont_ceux_de_la_table_des_droits() -> None:
    ecrivains = {lire_en_tete(fiche)["name"] for fiche in FICHES if ecrit(fiche)}

    assert ecrivains == set(DROITS_ECRITURE)


def test_les_agents_sans_outil_decriture_sont_ceux_de_la_liste_de_la_garde() -> None:
    lecteurs = {lire_en_tete(fiche)["name"] for fiche in FICHES if not ecrit(fiche)}

    assert lecteurs == set(AGENTS_SANS_ECRITURE)


def test_les_verificateurs_font_partie_des_agents_sans_ecriture() -> None:
    assert set(VERIFICATEURS) <= set(AGENTS_SANS_ECRITURE)


def test_le_hook_du_projet_surveille_les_outils_de_la_garde_et_bloque_en_cas_de_panne() -> None:
    reglages = json.loads((DEPOT / ".claude" / "settings.json").read_text(encoding="utf-8"))

    (groupe,) = reglages["hooks"]["PreToolUse"]
    (hook,) = groupe["hooks"]

    assert set(groupe["matcher"].split("|")) == OUTILS_SURVEILLES
    assert "backend/tools/garde_agents.py" in hook["command"]
    assert hook["command"].endswith("|| exit 2")
