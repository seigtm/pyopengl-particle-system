"""
Plane Attractor implementation for particle systems.

Implements a plane that attracts particles when they enter its range.
"""

import numpy as np
import OpenGL.GL as gl


class PlaneAttractor:
    """
    Represents a plane that attracts particles.

    The plane is defined by a point and a normal vector. When particles
    get within range, they are attracted towards the plane.
    """

    def __init__(self, position, normal, strength=1.0, range=5.0):
        """
        Initialize a plane attractor.

        Args:
            position (list): Point on the plane [x, y, z]
            normal (list): Normal vector of the plane [nx, ny, nz]
            strength (float): Attraction strength
            range (float): Maximum distance of influence
        """
        self.position = np.array(position, dtype=np.float32)

        # Normalize the normal vector
        normal_array = np.array(normal, dtype=np.float32)
        self.normal = normal_array / np.linalg.norm(normal_array)

        self.strength = strength
        self.range = range

        # Calculate plane equation coefficients (Ax + By + Cz + D = 0)
        self.A = self.normal[0]
        self.B = self.normal[1]
        self.C = self.normal[2]
        self.D = -np.dot(self.normal, self.position)

    def get_force(self, position):
        """
        Calculate the force applied to a particle at the given position.

        Args:
            position (np.array): 3D position vector of the particle

        Returns:
            np.array: 3D force vector
        """
        # Calculate signed distance from point to plane
        point = np.array(position)
        distance = self.A * point[0] + self.B * point[1] + self.C * point[2] + self.D

        # If outside of range, no force is applied
        if abs(distance) > self.range:
            return np.zeros(3)

        # Force is stronger as the particle gets closer to the plane
        # but within the range (inverse proportion to distance)
        force_magnitude = self.strength * (1.0 - abs(distance) / self.range)

        # Force direction is towards the plane (opposite of normal if above plane)
        force_direction = -np.sign(distance) * self.normal

        return force_magnitude * force_direction

    def draw(self):
        """Draw a representation of the plane attractor."""
        # Calculate plane corners for visualization
        # First find two vectors perpendicular to the normal
        v1 = np.array([1.0, 0.0, 0.0])
        if abs(np.dot(v1, self.normal)) > 0.9:
            v1 = np.array([0.0, 1.0, 0.0])
        v1 = v1 - np.dot(v1, self.normal) * self.normal
        v1 = v1 / np.linalg.norm(v1)

        v2 = np.cross(self.normal, v1)
        v2 = v2 / np.linalg.norm(v2)

        # Scale vectors to create a visible plane
        scale = 10.0
        v1 *= scale
        v2 *= scale

        # Calculate corners
        corners = [
            self.position + v1 + v2,
            self.position + v1 - v2,
            self.position - v1 - v2,
            self.position - v1 + v2,
        ]

        # Draw plane with semi-transparency
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        # Set material properties
        gl.glMaterialfv(gl.GL_FRONT, gl.GL_AMBIENT, [0.1, 0.1, 0.5, 0.3])
        gl.glMaterialfv(gl.GL_FRONT, gl.GL_DIFFUSE, [0.2, 0.2, 0.8, 0.3])
        gl.glMaterialfv(gl.GL_FRONT, gl.GL_SPECULAR, [0.4, 0.4, 1.0, 0.3])
        gl.glMaterialf(gl.GL_FRONT, gl.GL_SHININESS, 64.0)

        # Draw plane as a quad
        gl.glBegin(gl.GL_QUADS)
        gl.glNormal3f(*self.normal)
        for corner in corners:
            gl.glVertex3f(*corner)
        gl.glEnd()

        # Draw normal vector as a line
        gl.glDisable(gl.GL_LIGHTING)
        gl.glColor3f(1, 1, 0)  # Yellow
        gl.glBegin(gl.GL_LINES)
        gl.glVertex3f(*self.position)
        gl.glVertex3f(*(self.position + self.normal * 2))
        gl.glEnd()
        gl.glEnable(gl.GL_LIGHTING)
