"""
Camera controller for navigating 3D space with mouse.

Implements an orbiting camera that can be rotated with mouse drag
and zoomed with mouse wheel.
"""

import math
import numpy as np
import OpenGL.GLU as glu
import OpenGL.GLUT as glut


class Camera:
    """
    Orbiting camera controller.

    Allows navigation of 3D space by orbiting around a target point.
    """

    def __init__(self, distance=15.0, theta=30.0, phi=30.0):
        """
        Initialize camera with the given spherical coordinates.

        Args:
            distance (float): Distance from target
            theta (float): Horizontal angle in degrees
            phi (float): Vertical angle in degrees
        """
        self.distance = distance
        self.min_distance = 5.0
        self.max_distance = 30.0

        self.theta = theta  # Horizontal angle
        self.phi = phi  # Vertical angle

        self.target = np.array([0.0, 0.0, 0.0])

        # Mouse control state
        self.prev_x = 0
        self.prev_y = 0
        self.mouse_button = -1

    def handle_mouse_button(self, button, state, x, y):
        """
        Handle mouse button events.

        Args:
            button (int): Button identifier
            state (int): Button state (GLUT_DOWN or GLUT_UP)
            x, y (int): Mouse coordinates
        """
        if state == glut.GLUT_DOWN:
            self.mouse_button = button
            self.prev_x = x
            self.prev_y = y
        else:
            self.mouse_button = -1

    def handle_mouse_motion(self, x, y):
        """
        Handle mouse motion events for camera rotation.

        Args:
            x, y (int): Current mouse coordinates
        """
        if self.mouse_button != glut.GLUT_LEFT_BUTTON:
            return

        # Calculate mouse movement deltas
        dx = x - self.prev_x
        dy = y - self.prev_y

        # Update camera angles
        self.theta += dx * 0.5
        self.phi += dy * 0.5

        # Clamp vertical angle to avoid gimbal lock
        self.phi = max(-85, min(85, self.phi))

        # Remember current mouse position
        self.prev_x = x
        self.prev_y = y

    def handle_mouse_wheel(self, direction):
        """
        Handle mouse wheel events for camera zoom.

        Args:
            direction (int): Direction of wheel movement
        """
        # Adjust camera distance
        zoom_factor = 1.1
        if direction > 0:
            self.distance /= zoom_factor
        else:
            self.distance *= zoom_factor

        # Clamp distance to reasonable range
        self.distance = max(self.min_distance, min(self.max_distance, self.distance))

    def apply(self):
        """Apply camera transformation to current OpenGL modelview matrix."""
        # Convert spherical coordinates to Cartesian
        theta_rad = math.radians(self.theta)
        phi_rad = math.radians(self.phi)

        x = self.distance * math.sin(theta_rad) * math.cos(phi_rad)
        y = self.distance * math.sin(phi_rad)
        z = self.distance * math.cos(theta_rad) * math.cos(phi_rad)

        # Set camera position and orientation
        glu.gluLookAt(
            x,
            y,
            z,  # Camera position
            *self.target,  # Target/look-at point
            0.0,
            1.0,
            0.0  # Up vector
        )
