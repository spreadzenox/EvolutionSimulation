## Evolution Simulation

This project simulates an environment where "blobs" interact with their world, evolve, and adapt over time. The simulation exposes parameters for food, reproduction, mutation, energy, and perception, letting blobs move, eat, reproduce, and mutate based on a compact neural network.

### Requirements

- Python 3.8+
- pygame
- numpy

Install dependencies:

```bash
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

### Core Modules

- `evolution_simulation/game.py`: main game loop and UI wiring
- `evolution_simulation/entities.py`: `Grid`, `Blob`, `Food`, `Brain`
- `evolution_simulation/ui.py`: sliders, monitor, image manager, UI widgets
- `evolution_simulation/constants.py`: tunable constants and colors
- `evolution_simulation/utils.py`: utility functions (e.g., density scan)

### Features

- Blob movement, eating, reproduction with mutation
- Simple neural network controller per blob
- Real-time sliders for parameters and target FPS
- Lightweight monitoring (population, energy, behaviours)

### Controls

- Space: pause/resume simulation
- UI sliders: adjust parameters and FPS in real time

### Future work

- Advanced mutation strategies
- Additional environmental factors
- Richer visualisation and analytics
