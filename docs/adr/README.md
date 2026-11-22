# Décisions d'architecture (ADR)

Chaque décision structurante est consignée ici : son contexte, la décision prise, les alternatives écartées et ses conséquences. Une décision n'est jamais réécrite ; si elle change, on rédige un nouvel ADR qui la remplace.

| N° | Décision | Statut |
|---|---|---|
| [0001](0001-monolithe-modulaire-hexagonal.md) | Monolithe modulaire en architecture hexagonale allégée | Accepté |
| [0002](0002-persistance-sqlalchemy-imperatif-uow.md) | Persistance : SQLAlchemy synchrone, mapping impératif, Unit of Work | Accepté |
| [0003](0003-authentification.md) | Authentification, sessions et invitations | Accepté |
| [0004](0004-traitement-des-fichiers.md) | Envoi, contrôle et stockage des fichiers | Accepté |
| [0005](0005-design-patterns-et-garde-fous.md) | Design patterns, SOLID et garde-fous contre le code spaghetti | Accepté |
| [0006](0006-code-partage-entre-fonctionnalites-frontend.md) | Code partagé entre fonctionnalités du frontend : `src/api` | Accepté |
