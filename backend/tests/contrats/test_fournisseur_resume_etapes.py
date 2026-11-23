"""Contrat du port `FournisseurResumeEtapes` de chantiers : joué sur ses deux implémentations.

Il porte sur la forme du résultat : une entrée par chantier demandé, et le résumé
nul pour un chantier sans étape. Le calcul lui-même est testé dans le module étapes.
"""

from uuid import UUID

from app.chantiers.application.ports import RESUME_SANS_ETAPE, FournisseurResumeEtapes

CHANTIERS = [UUID(int=1), UUID(int=2), UUID(int=3)]


def test_chaque_chantier_demande_a_exactement_une_entree(
    fournisseur_resume: FournisseurResumeEtapes,
) -> None:
    resumes = fournisseur_resume.executer(CHANTIERS)

    assert set(resumes) == set(CHANTIERS)


def test_un_chantier_sans_etape_a_le_resume_nul(
    fournisseur_resume: FournisseurResumeEtapes,
) -> None:
    resumes = fournisseur_resume.executer(CHANTIERS[:1])

    assert resumes == {CHANTIERS[0]: RESUME_SANS_ETAPE}


def test_sans_chantier_demande_le_resultat_est_vide(
    fournisseur_resume: FournisseurResumeEtapes,
) -> None:
    assert dict(fournisseur_resume.executer([])) == {}
