"""Retire des adresses déjà enregistrées les caractères que le domaine refuse désormais.

Le lot S8 a durci le contrôle des textes saisis (`app.shared.domain.caracteres`) : sont
refusés en plus les séparateurs de ligne et de paragraphe, les caractères d'usage privé et
la plupart des caractères de mise en forme invisibles (comme l'espace sans chasse), et un
texte obligatoire doit contenir un caractère visible. Or lire un chantier reconstruit son
adresse par le constructeur de l'objet valeur `Adresse`, donc par ces contrôles. Une adresse
enregistrée avant ce lot et contenant un tel caractère ferait échouer sa lecture, et avec
elle celle de la liste de tous les chantiers (erreur 500 sur la page d'accueil de la démo).
Cette migration nettoie les données avant que l'application ne les relise.

Seules les colonnes de l'adresse sont concernées : l'adresse est le seul objet valeur
composite relu par son constructeur. Le nom, le client et les titres sont recopiés tels
quels à la lecture, sans repasser par les contrôles : ils s'affichent encore, et leurs
anciennes valeurs ne cassent rien.

Les règles de nettoyage sont recopiées ici, de façon figée, et n'importent pas le domaine :
une migration décrit un instant précis du schéma et des données, alors que les règles du
domaine évolueront. Importer le domaine ferait changer, avec lui, le résultat d'une
migration déjà appliquée ailleurs.

Pour chaque partie de l'adresse (voie, code postal, ville) :
- un saut de ligne ou une tabulation (contrôle), un séparateur de ligne ou de paragraphe
  devient une espace : les retirer collerait les deux mots voisins ;
- un caractère d'usage privé ou de mise en forme (hors la liste admise, qui garde le liant
  des emojis et les drapeaux) est retiré ;
- si le texte a changé, les espaces de début et de fin sont retirées, puisque le nettoyage
  a pu en créer ;
- si le texte ne contient alors plus aucun caractère visible, il est remplacé par
  `VALEUR_NEUTRE`. Elle tient en 10 caractères, la longueur maximale du code postal, et dit
  clairement qu'une saisie est à refaire. Elle sert aussi à un champ qui était déjà fait
  seulement d'espaces ou de liants.

Une adresse sans caractère refusé n'est pas modifiée, et la migration est rejouable : un
second passage ne trouve plus rien à nettoyer. Les adresses des chantiers ne sont jamais
supprimées, seuls des caractères le sont : c'est une perte de données, signalée ici.

Cette purge est irréversible : `downgrade` ne change rien, car les caractères retirés ne
peuvent pas être retrouvés (et les rétablir réintroduirait des adresses illisibles).

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-25
"""

import unicodedata
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: str | Sequence[str] | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Texte mis à la place d'une partie d'adresse sans caractère visible. 10 caractères : la
# longueur maximale du code postal, la plus courte des trois parties.
VALEUR_NEUTRE = "À préciser"

# Règles du domaine à la date du lot S8, recopiées (voir le début de ce fichier).
# Les contrôles et les séparateurs de ligne ou de paragraphe deviennent une espace.
CATEGORIES_REMPLACEES_PAR_UNE_ESPACE = frozenset({"Cc", "Zl", "Zp"})
# Usage privé, demi-codets isolés et mise en forme : retirés.
CATEGORIES_RETIREES = frozenset({"Co", "Cs", "Cf"})
# Mise en forme admise malgré sa catégorie : antiliant et liant sans chasse, marques de
# sens (U+200C à U+200F) et caractères d'étiquette des drapeaux (U+E0020 à U+E007F).
MISE_EN_FORME_ADMISE = frozenset(
    chr(code) for code in (*range(0x200C, 0x2010), *range(0xE0020, 0xE0080))
)
# Catégories dont aucun caractère ne se voit à lui seul : espaces, séparateurs, contrôles,
# mise en forme et marques combinantes.
CATEGORIES_INVISIBLES = frozenset({"Zs", "Zl", "Zp", "Cc", "Cf", "Mn", "Mc", "Me"})

CHANTIERS = sa.table(
    "chantiers",
    sa.column("id", sa.Uuid()),
    sa.column("voie", sa.String()),
    sa.column("code_postal", sa.String()),
    sa.column("ville", sa.String()),
)
COLONNES_DE_L_ADRESSE = ("voie", "code_postal", "ville")


def _sans_caracteres_refuses(texte: str) -> str:
    """Remplace ou retire les caractères refusés ; rend le texte tel quel s'il n'en a pas."""
    resultat = []
    for caractere in texte:
        categorie = unicodedata.category(caractere)
        if caractere in MISE_EN_FORME_ADMISE:
            resultat.append(caractere)
        elif categorie in CATEGORIES_REMPLACEES_PAR_UNE_ESPACE:
            resultat.append(" ")
        elif categorie not in CATEGORIES_RETIREES:
            resultat.append(caractere)
    nettoye = "".join(resultat)
    return texte if nettoye == texte else nettoye.strip()


def _contient_un_caractere_visible(texte: str) -> bool:
    return any(unicodedata.category(caractere) not in CATEGORIES_INVISIBLES for caractere in texte)


def _corriger(texte: str) -> str:
    """Rend le texte nettoyé, ou `VALEUR_NEUTRE` s'il ne reste aucun caractère visible."""
    nettoye = _sans_caracteres_refuses(texte)
    return nettoye if _contient_un_caractere_visible(nettoye) else VALEUR_NEUTRE


def upgrade() -> None:
    """Nettoie la voie, le code postal et la ville des chantiers qui en ont besoin."""
    connexion = op.get_bind()
    lignes = list(connexion.execute(sa.select(CHANTIERS)).mappings())
    for ligne in lignes:
        corrigees = {colonne: _corriger(ligne[colonne]) for colonne in COLONNES_DE_L_ADRESSE}
        if corrigees != {colonne: ligne[colonne] for colonne in COLONNES_DE_L_ADRESSE}:
            connexion.execute(
                sa.update(CHANTIERS).where(CHANTIERS.c.id == ligne["id"]).values(**corrigees)
            )


def downgrade() -> None:
    """Ne fait rien : la purge est irréversible, les caractères retirés sont perdus."""
