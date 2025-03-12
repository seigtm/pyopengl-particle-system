# Python OpenGL Particle System Simulation

This project demonstrates a particle system simulation with a cylindrical emitter, particle trails, and plane attractor interaction using OpenGL.

## Features

- Cylindrical particle emitter with adjustable number of particles (50-500)
- Particle trails with adjustable length (1-10 positions)
- Transparency that changes based on particle lifetime
- Plane attractor that influences particle movement
- Interactive camera controls
- Real-time parameter display

## Requirements

- Python 3.x
- NumPy
- PyOpenGL
- PyOpenGL-accelerate (optional, but recommended)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
python main.py
```

### Controls

- **H**: Toggle help display
- **P**: Pause simulation
- **E**: Toggle emitter visibility
- **A**: Toggle attractor visibility
- **Space**: Toggle attractor activation
- **R**: Reset particles
- **Up/Down Arrows**: Increase/decrease particle count by 50
- **Left/Right Arrows**: Decrease/increase trail length
- **Mouse drag**: Rotate view
- **Mouse wheel**: Zoom in/out

## Implementation Details

### Particle System

- Particles are emitted from the surface of a cylinder
- Each particle has:
  - Position and velocity
  - Size and color
  - Transparency that decreases with lifetime
  - Trail showing recent positions

### Physics

- Particles move based on their velocity
- Plane attractor influences particles within its range
- Attraction force increases as particles get closer to the plane

### Visualization

- Particles are rendered as points
- Trails are rendered as line segments with decreasing opacity
- Cylindrical emitter is shown as a wireframe
- Plane attractor is shown as a semi-transparent surface

## Documentation

For detailed technical explanation (in Russian), see [`detailed_explanation_ru.md`](./docs/detailed_explanation_ru.md).
