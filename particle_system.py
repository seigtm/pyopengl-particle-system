"""
Particle System implementation for OpenGL.

Implements a particle system with:
- Cylindrical emitter
- Particles with variable transparency based on lifetime
- Particle trails
- Interaction with attractors
"""

import numpy as np
import random
import math
import OpenGL.GL as gl


class Particle:
    """Represents a single particle in the system."""

    def __init__(self, position, velocity, size, color, lifetime, max_lifetime):
        """
        Initialize a particle with given properties.

        Args:
            position (np.array): 3D position vector
            velocity (np.array): 3D velocity vector
            size (float): Particle size/radius
            color (list): RGBA color
            lifetime (float): Current lifetime in seconds
            max_lifetime (float): Maximum lifetime in seconds
        """
        self.position = position.copy()
        self.velocity = velocity.copy()
        self.size = size
        self.color = color.copy()
        self.lifetime = lifetime
        self.max_lifetime = max_lifetime

        # Initialize trail as a list of past positions
        self.trail = [position.copy()]

    def update(self, dt, attractor=None):
        """
        Update particle state.

        Args:
            dt (float): Time step in seconds
            attractor: Optional attractor affecting the particle

        Returns:
            bool: True if particle is still alive, False if expired
        """
        # Apply attractor influence if provided
        if attractor:
            attraction_force = attractor.get_force(self.position)
            self.velocity = self.velocity + attraction_force * dt

        # Update position based on velocity
        self.position = self.position + self.velocity * dt

        # Store position for trail (only keep the most recent positions)
        self.trail.append(self.position.copy())

        # Update lifetime
        self.lifetime -= dt

        # Update alpha based on remaining lifetime proportion
        life_ratio = self.lifetime / self.max_lifetime
        self.color[3] = life_ratio  # Alpha channel

        # Return True if particle is still alive
        return self.lifetime > 0

    def reset_trail(self, max_length):
        """
        Reset trail to only contain current position.

        Args:
            max_length (int): Maximum trail length to keep
        """
        if len(self.trail) > max_length:
            self.trail = self.trail[-max_length:]


class ParticleSystem:
    """Manages a system of particles emitted from a cylindrical surface."""

    def __init__(
        self, count=200, trail_length=4, emitter_radius=1.0, emitter_height=2.0
    ):
        """
        Initialize the particle system.

        Args:
            count (int): Number of particles to generate
            trail_length (int): Length of particle trails
            emitter_radius (float): Radius of cylindrical emitter
            emitter_height (float): Height of cylindrical emitter
        """
        self.count = count
        self.trail_length = trail_length
        self.emitter_radius = emitter_radius
        self.emitter_height = emitter_height

        # Particle properties ranges
        self.min_size = 0.05
        self.max_size = 0.15
        self.min_speed = 0.5
        self.max_speed = 2.0
        self.min_lifetime = 3.0
        self.max_lifetime = 8.0

        # Create initial particles
        self.particles = []
        self.reset()

    def reset(self):
        """Reset and recreate all particles."""
        self.particles = []

        for _ in range(self.count):
            # Create a new particle with random properties
            self.particles.append(self.create_particle())

    def create_particle(self):
        """
        Create a new particle at a random position on the cylinder surface.

        Returns:
            Particle: A new particle instance
        """
        # Random angle around cylinder
        angle = random.uniform(0, 2 * math.pi)

        # Random height along cylinder
        height = random.uniform(-self.emitter_height / 2, self.emitter_height / 2)

        # Position on cylinder surface
        x = self.emitter_radius * math.cos(angle)
        y = height
        z = self.emitter_radius * math.sin(angle)
        position = np.array([x, y, z])

        # Calculate normal at cylinder surface (points outward from center)
        normal = np.array([math.cos(angle), 0, math.sin(angle)])

        # Random speed
        speed = random.uniform(self.min_speed, self.max_speed)

        # Velocity based on normal direction
        velocity = normal * speed

        # Random size
        size = random.uniform(self.min_size, self.max_size)

        # Random color with full alpha
        color = [
            random.uniform(0.3, 1.0),  # R
            random.uniform(0.3, 1.0),  # G
            random.uniform(0.3, 1.0),  # B
            1.0,  # A (starts fully opaque)
        ]

        # Random lifetime
        max_lifetime = random.uniform(self.min_lifetime, self.max_lifetime)

        return Particle(position, velocity, size, color, max_lifetime, max_lifetime)

    def update(self, dt, attractor=None):
        """
        Update all particles in the system.

        Args:
            dt (float): Time step in seconds
            attractor: Optional attractor affecting particles
        """
        # Temporary list for alive particles
        alive_particles = []

        for particle in self.particles:
            # Update the particle
            if particle.update(dt, attractor):
                # Keep alive particles
                particle.reset_trail(self.trail_length)
                alive_particles.append(particle)
            else:
                # Replace dead particles with new ones
                alive_particles.append(self.create_particle())

        self.particles = alive_particles

    def draw(self):
        """Draw all particles and their trails."""
        # Disable lighting for particles
        gl.glDisable(gl.GL_LIGHTING)

        # Draw trails first (lines)
        gl.glBegin(gl.GL_LINES)
        for particle in self.particles:
            if len(particle.trail) > 1:
                # Use particle color with decreasing alpha for trail segments
                trail_alpha_step = particle.color[3] / len(particle.trail)

                for i in range(len(particle.trail) - 1):
                    # Calculate alpha for this segment
                    alpha = particle.color[3] - (i * trail_alpha_step)

                    # Set color with calculated alpha
                    gl.glColor4f(
                        particle.color[0], particle.color[1], particle.color[2], alpha
                    )

                    # Draw line segment
                    gl.glVertex3f(*particle.trail[i])
                    gl.glVertex3f(*particle.trail[i + 1])
        gl.glEnd()

        # Draw particles as points
        gl.glEnable(gl.GL_POINT_SMOOTH)
        gl.glPointSize(8.0)
        gl.glBegin(gl.GL_POINTS)
        for particle in self.particles:
            gl.glColor4f(*particle.color)
            gl.glVertex3f(*particle.position)
        gl.glEnd()

        # Re-enable lighting
        gl.glEnable(gl.GL_LIGHTING)
