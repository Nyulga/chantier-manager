"""Contrat du port `GenerateurId` : joué sur les UUID v7 et sur le générateur prévisible.

Les repositories listent « dans l'ordre de création » en triant par identifiant :
les deux implémentations doivent donc distribuer des identifiants croissants.
"""

from app.shared.application.ports import GenerateurId

NOMBRE_D_IDENTIFIANTS = 100


def test_les_identifiants_sont_uniques_et_strictement_croissants(
    generateur_id: GenerateurId,
) -> None:
    identifiants = [generateur_id.nouveau() for _ in range(NOMBRE_D_IDENTIFIANTS)]

    assert identifiants == sorted(set(identifiants))
