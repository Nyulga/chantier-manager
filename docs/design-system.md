# Design system « Balise »

- **Statut** : validé le 2026-11-22
- **Maquette de référence** : https://claude.ai/artifact/KX1S3PrVSjSJ77CwFUehWu (privée, accessible au propriétaire du projet)

Ce document est la référence visuelle du frontend. Ces tokens seront implémentés dans le thème Tailwind au lot 01 ; aucune couleur, taille ou police ne doit être écrite en dur en dehors de ce thème.

## 1. Principe

Le langage visuel est celui de la **signalisation de chantier** : du jaune haute visibilité, du graphite, et des titres condensés comme sur un panneau.

> **Règle d'or : le jaune haute visibilité et les rayures sont réservés à ce qui attend une action du chef de chantier**, c'est-à-dire aux étapes « à valider ».
> Le jaune sert aussi au bouton d'action principal des écrans mobiles et à l'élément actif de la navigation. Il ne sert à rien d'autre : ni à la décoration, ni aux barres d'avancement, ni aux liens.

## 2. Couleurs

### 2.1 Thème clair (par défaut)

| Token | Valeur | Usage |
|---|---|---|
| `bg` | `#F1F0EC` | Fond de page (« béton ») |
| `surface` | `#FFFFFF` | Cartes, listes, champs |
| `fg` | `#1F2124` | Texte principal, barre latérale, boutons d'action sur ordinateur (« graphite ») |
| `muted` | `#5A5D62` | Texte secondaire, métadonnées |
| `line` | `#D6D4CE` | Bordures |
| `line-soft` | `#EBE9E4` | Séparateurs internes |
| `accent` | `#F2A900` | Jaune haute visibilité (voir la règle d'or) |
| `on-accent` | `#1F2124` | Texte sur fond jaune |
| `accent-ink` | `#855600` | Liens, et tout texte qui doit évoquer l'accent sur fond clair |
| `accent-soft` | `#FFF8E6` | Fond d'une ligne « à valider » |
| `danger` | `#B42318` | Refus, retard, erreurs |
| `danger-soft` | `#FBE4E1` | Fond des badges « en retard » |

### 2.2 Thème sombre

| Token | Valeur |
|---|---|
| `bg` | `#17191C` |
| `surface` | `#202327` |
| `fg` | `#ECEBE7` |
| `muted` | `#A4A7AC` |
| `line` | `#353940` |
| `accent` / `accent-ink` | `#F5B521` |
| `on-accent` | `#17191C` |
| `accent-soft` | `#2A2412` |
| `danger` | `#F0716A` |
| `danger-soft` | `#3A1D1B` |

Le thème suit le réglage du système (`prefers-color-scheme`), et l'utilisateur peut le forcer.

### 2.3 Statuts d'étape

| Statut | Clair (fond / texte) | Sombre (fond / texte) |
|---|---|---|
| À faire | `#E7E6E2` / `#3D4045` | `#2C2F34` / `#C9CBCF` |
| En cours | `#DDE8F6` / `#1D4F8C` | `#1D3352` / `#9CC3F5` |
| À valider | `#F2A900` / `#1F2124` | `#F5B521` / `#17191C` |
| Validée | `#DCEFE1` / `#1C6B34` | `#183823` / `#8FD6A4` |

- Le statut s'écrit toujours **en toutes lettres** dans le badge ; il n'est jamais transmis par la seule couleur.
- Tous les couples texte/fond respectent un contraste d'au moins 4,5:1 (WCAG AA).

## 3. Typographie

| Rôle | Police | Réglages |
|---|---|---|
| Titres | **Archivo** condensé | `font-stretch: 72%`, graisse 800, MAJUSCULES, `letter-spacing: .01em` |
| Texte | **Archivo** | graisses 400, 500, 600 et 700 |
| Références et données | **IBM Plex Mono** | Références de chantier (`CH-2026-014`), numéros d'étape, horodatages |

Les polices sont **auto-hébergées** avec le frontend, et non chargées depuis Google Fonts. Cela évite d'envoyer l'adresse IP des visiteurs à un tiers (RGPD) et respecte la CSP stricte.

Échelle typographique, en px :

| Usage | Taille |
|---|---|
| Titre de page (ordinateur) | 40–44 |
| Titre de page (mobile) | 28 |
| Titre de section | 24 |
| Titre de carte | 19–21 |
| Texte | 15–16 |
| Secondaire | 13–14 |
| Étiquettes | 12 |

- Le texte de base fait **16 px sur mobile**.
- Les chiffres alignés utilisent `font-variant-numeric: tabular-nums`.

## 4. Formes et espacements

- **Rayon** : 4 px pour les boutons, champs et cartes ; 6 px pour les badges ; 50 % pour les avatars.
- **Espacements** : multiples de 4 px (4, 8, 12, 16, 20, 24, 28, 32, 40).
- **Ombres** : aucune. La hiérarchie passe par le fond (`bg` ou `surface`) et les bordures.
- **Rayures « balise »** : `repeating-linear-gradient(135deg, accent 0 8px, fg 8px 16px)`, en bandeau de 8 px. On les utilise uniquement :
  - en haut du bloc « À valider » ;
  - sur le bord gauche d'une étape à valider ;
  - dans le logo.

## 5. Composants

| Composant | Règles |
|---|---|
| **Bouton principal** | Sur ordinateur : fond `fg`, texte blanc. Sur mobile : fond `accent`, texte `on-accent`. Graisse 700 ou 800. |
| **Bouton secondaire** | Fond `surface`, bordure `line`. |
| **Bouton de refus** | Fond transparent, bordure et texte `danger`. |
| **Hauteur minimale** | 44 px sur ordinateur, **52 à 56 px sur mobile** (utilisable avec des gants). |
| **Champ** | Hauteur 44 px (52 px sur mobile), bordure `line`, focus avec une bordure de 2 px `fg`. Le libellé est toujours visible au-dessus du champ ; l'erreur s'affiche en dessous, en `danger`, et explique comment corriger. |
| **Badge de statut** | Voir §2.3 ; graisse 700, 12,5 px. |
| **Barre d'avancement** | Hauteur 10 px, piste `#E7E6E2`, remplissage `fg` (jamais `accent`), toujours accompagnée du texte « x / y étapes · z % ». |
| **Carte chantier** | Référence en mono, nom en titre condensé, adresse, badge de synthèse, barre d'avancement, échéance avec le compte à rebours (J-54), ou « En retard de n jours » en `danger`. |
| **Ligne à valider** | Bord gauche rayé, fond `accent-soft`, auteur, date et note de l'ouvrier, puis les actions Valider, Refuser et Voir les photos. |
| **Navigation (ordinateur)** | Barre latérale graphite ; élément actif sur fond `accent`. |
| **Navigation (mobile)** | Barre d'onglets en bas de l'écran (Étapes, Notes, Photos et docs) et bouton « Prendre une photo » toujours accessible. |
| **Focus clavier** | Toujours visible : contour de 3 px, décalé de 2 px. |

## 6. Règles d'écriture

- L'interface est en français et **tutoie** l'utilisateur, comme dans la maquette (« Ton étape en cours », « Demande une invitation à ton chef de chantier »).
- Un bouton dit exactement ce qu'il fait : « Valider l'étape », « Envoyer le refus », « Signaler terminée ».
- Les messages de confirmation disent ce qui va se passer ensuite. Exemple : « C'est envoyé. Julien Moreau doit maintenant valider l'étape. »
- Dates au format `JJ/MM/AAAA` ; montants au format `18 450,00 €` (espace insécable).
