
# Evolution Simulation

Ce projet simule un environnement où des "blobs" interagissent avec leur environnement, évoluent et s'adaptent au fil du temps. La simulation comprend divers paramètres pour la nourriture, la reproduction, la mutation et l'énergie, permettant aux blobs de se déplacer, manger, se reproduire et muter en fonction de leur comportement contrôlé par un réseau neuronal.

## Pré-requis

- Python 3.x
- Pygame
- Numba
- Numpy

Installez les bibliothèques requises en utilisant :

```bash
pip install pygame numba numpy
```

## Paramètres de simulation

La simulation fonctionne avec les paramètres suivants :

- **Framerate:** 30 FPS
- **Niveaux d'énergie:** Contrôle la survie, les mouvements et la reproduction des blobs
- **Taux de mutation:** Définit la fréquence des mutations
- **Apparition et consommation de nourriture:** Les blobs consomment de la nourriture pour survivre et gagner de l'énergie
- **Reproduction:** Basée sur les niveaux d'énergie, les blobs peuvent se reproduire avec des mutations possibles chez les descendants
- **Taille de la grille:** 400x400 cellules
- **Taille de la fenêtre:** 900x900 pixels

## Aperçu des classes

### `Grid`
Gère les blobs et la nourriture sur la grille. Il s'occupe de l'apparition des aliments, de l'instanciation des blobs et des mises à jour des données.

### `Blob`
Représente un blob individuel dans la simulation. Les blobs peuvent se déplacer, manger, se reproduire et muter. Chaque blob possède un réseau neuronal (`Brain`) qui détermine ses actions en fonction de l'environnement.

### `Brain`
Le réseau neuronal qui contrôle les actions du blob. Il traite les entrées environnementales (comme la nourriture ou les autres blobs à proximité) et produit une sortie qui détermine la prochaine action du blob.

### `Food`
Représente la nourriture que les blobs consomment pour gagner de l'énergie. La nourriture a une quantité d'énergie, une taille et une couleur qui changent lorsqu'elle est consommée.

### `Button`
Utilisé pour créer des boutons interactifs dans la fenêtre de simulation (ex. bouton pause).

## Fonctionnalités principales

- **Déplacement des blobs:** Les blobs se déplacent sur la grille en fonction des prédictions de leur réseau neuronal.
- **Manger:** Les blobs mangent de la nourriture à portée pour gagner de l'énergie.
- **Reproduction:** Lorsque les blobs ont suffisamment d'énergie, ils se reproduisent en transmettant leur réseau neuronal aux descendants, avec des mutations potentielles.
- **Réseau neuronal (Brain):** Chaque blob possède un réseau neuronal qui détermine son comportement en fonction des entrées de son environnement.
- **Graphismes et HUD:** Affiche le comportement des blobs, leur énergie et des statistiques générales pendant la simulation.

## Comment exécuter

1. Assurez-vous que les bibliothèques requises sont installées.
2. Exécutez la fonction `main()` pour démarrer la simulation.
3. Observez les blobs qui se déplacent, mangent, se reproduisent et évoluent au fil du temps.

```bash
python maiin.py
```

## Contrôles

- **Bouton Pause:** Situé en haut de la fenêtre, permet de mettre en pause et de reprendre la simulation.
- **Interaction avec la souris:** Passez la souris sur les blobs pour voir les détails sur leur comportement et leurs niveaux d'énergie.

## Améliorations futures

- Implémenter des stratégies de mutation plus avancées.
- Ajouter plus de facteurs environnementaux affectant la survie des blobs.
- Améliorer la visualisation avec des statistiques plus détaillées.
