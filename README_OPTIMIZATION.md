# Evolution Simulation – Optimizations

## Key optimizations

### 1) Adjustable FPS slider

- Interactive slider to control simulation speed (1–120 FPS)
- Shows current FPS and target FPS

### 2) Caching for scans

- Per-blob cache of recent scans
- Smart invalidation when grid changes
- Avoids repeated, expensive neighbourhood scans

### 3) Distance and loop optimization

- Manhattan distance (abs(i)+abs(j))
- Precomputed iter bounds to reduce modulo/branching

### 4) Density helpers

- Fast directional density for food/blobs with clamping to [0,1]

### 5) Render scheduling

- Separate simulation update cadence vs. render loop
- UI capped at 60 FPS

### 6) Reproduction simplification

- Balanced energy transfer and occasional mutation

## Behavioural tweaks

- Normalized inputs to the policy network
- Light random exploration noise
- Adaptive penalties to break local loops
- Energy-dependent softmax temperature
- Attack cooldown and kin penalty

## Results

- Fewer redundant computations (scan caching)
- Smoother UI at higher blob counts
- More varied behaviours over time
