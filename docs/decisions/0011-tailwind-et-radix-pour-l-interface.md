# ADR 0011 – Tailwind CSS et Radix pour l'interface

- **Statut** : accepté
- **Date** : 2026-11-24 (hors lot). Le choix est fait dans `intent.md` (section frontend). Tailwind est en place depuis le lot S1 ; Radix ne l'est pas encore.

## Contexte
L'interface doit appliquer le design system Balise (`docs/design-system.md`), sans couleur ni taille écrite en dur. Elle doit aussi être accessible au niveau WCAG 2.1 AA, en français, et pensée d'abord pour le mobile. Les composants interactifs complexes (menus, boîtes de dialogue, listes déroulantes) sont difficiles à rendre accessibles quand on les écrit soi-même : focus, clavier, lecteurs d'écran.

## Décision
- **Tailwind CSS** porte les tokens de Balise. Ils sont déclarés une seule fois, dans `src/ui/theme/balise.css` (`@theme`). Les composants de `src/ui` n'utilisent que ces tokens : les valeurs arbitraires comme `bg-[#F2A900]` sont interdites (règle 05).
- **Radix** fournira les composants interactifs complexes, accessibles par défaut et sans style imposé. Le style reste celui de Balise.
  - **Pas encore installé** : les composants du squelette (bouton, champ, carte, navigation…) sont du HTML natif, déjà accessible.
  - **Installation** : Radix sera installé au premier composant qui en a besoin, par exemple une boîte de dialogue ou un menu.
- **Seul `src/ui` importe Tailwind et Radix** (règle 05). Les pages n'assemblent que des composants de `ui`.

## Alternatives écartées
- **CSS écrit à la main (ou CSS Modules)** : les tokens risqueraient d'être recopiés d'un fichier à l'autre, sans contrôle qui interdise une couleur en dur.
- **Une bibliothèque de composants déjà stylés (MUI, Chakra, Bootstrap)** : il faudrait combattre son style pour appliquer Balise. Elle alourdit aussi la page sur mobile.
- **Headless UI** : même idée que Radix, mais avec moins de composants. Radix couvre mieux les besoins prévus (menus, onglets, info-bulles).
- **Écrire soi-même les composants interactifs complexes** : le risque d'erreur d'accessibilité est élevé, et le travail serait refait pour chacun.

## Conséquences
- **En bien** : le design system n'a qu'une source (le thème), le lint peut refuser une valeur en dur, et l'accessibilité des composants complexes vient d'une bibliothèque éprouvée.
- **En mal** : les classes Tailwind allongent le JSX. L'arrivée de Radix ajoutera une dépendance, à justifier dans le rapport de l'étape qui l'installe (règle 00, sobriété).
