"""
Particle System Simulation

This application demonstrates a particle system with:
- Cylindrical emitter
- Particles with trails and changing transparency
- Plane attractor affecting particle movement
"""

import sys

import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.GLUT as glut

from particle_system import ParticleSystem
from plane_attractor import PlaneAttractor
from camera import Camera


def render_text(text, x, y):
    """
    Renders 2D text overlay on the scene.
    Uses GLUT bitmap fonts and temporarily switches to orthographic projection.

    Args:
        text (str): Text to render
        x, y (int): Screen coordinates for text position
    """
    # Disable 3D features
    gl.glDisable(gl.GL_LIGHTING)
    gl.glDisable(gl.GL_DEPTH_TEST)

    # Switch to 2D orthographic projection
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPushMatrix()
    gl.glLoadIdentity()
    gl.glOrtho(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, -1, 1)

    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glPushMatrix()
    gl.glLoadIdentity()

    # Render text
    gl.glColor3f(1, 1, 1)
    gl.glRasterPos2i(x, y)
    for ch in text:
        glut.glutBitmapCharacter(glut.GLUT_BITMAP_8_BY_13, ord(ch))

    # Restore previous state
    gl.glPopMatrix()
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glPopMatrix()
    gl.glMatrixMode(gl.GL_MODELVIEW)

    # Re-enable 3D features
    gl.glEnable(gl.GL_LIGHTING)
    gl.glEnable(gl.GL_DEPTH_TEST)


class ParticleSimulation:
    """Main class for the particle system simulation."""

    def __init__(self):
        """Initialize the simulation state and parameters."""
        # Particle system configuration
        self.particle_count = 200  # Number of particles
        self.min_particles = 50
        self.max_particles = 500

        self.trail_length = 4  # Length of particle trails
        self.min_trail_length = 1
        self.max_trail_length = 10

        # Create particle system with cylindrical emitter
        self.particle_system = ParticleSystem(
            count=self.particle_count,
            trail_length=self.trail_length,
            emitter_radius=2.0,
            emitter_height=4.0,
        )

        # Create plane attractor
        self.attractor = PlaneAttractor(
            position=[0, -5, 0], normal=[0, 1, 0], strength=0.5, range=8.0
        )

        # Camera control
        self.camera = Camera()

        # UI state
        self.paused = False
        self.show_help = True
        self.show_emitter = True
        self.show_attractor = True
        self.attractor_active = True

    def change_particle_count(self, delta):
        """
        Change the number of particles by the given delta.

        Args:
            delta (int): Amount to change particle count by
        """
        # Update particle count within limits
        self.particle_count = max(
            self.min_particles, min(self.max_particles, self.particle_count + delta)
        )

        # Create new particle system with updated count
        self.particle_system = ParticleSystem(
            count=self.particle_count,
            trail_length=self.trail_length,
            emitter_radius=self.particle_system.emitter_radius,
            emitter_height=self.particle_system.emitter_height,
        )

    def change_trail_length(self, delta):
        """
        Change the trail length by the given delta.

        Args:
            delta (int): Amount to change trail length by
        """
        # Update trail length within limits
        self.trail_length = max(
            self.min_trail_length, min(self.max_trail_length, self.trail_length + delta)
        )

        # Update trail length in existing particle system
        self.particle_system.trail_length = self.trail_length

        # Reset trails to apply new length
        for particle in self.particle_system.particles:
            particle.reset_trail(self.trail_length)

    def init_gl(self):
        """Initialize OpenGL state."""
        gl.glClearColor(0.05, 0.05, 0.1, 1.0)
        gl.glEnable(gl.GL_DEPTH_TEST)

        # Enable blending for transparency
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        # Enable point smoothing
        gl.glEnable(gl.GL_POINT_SMOOTH)
        gl.glHint(gl.GL_POINT_SMOOTH_HINT, gl.GL_NICEST)

        # Enable lighting for cylinder and plane visualization
        gl.glEnable(gl.GL_LIGHTING)
        gl.glEnable(gl.GL_LIGHT0)
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, [10, 10, 10, 1])
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_DIFFUSE, [1, 1, 1, 1])
        gl.glLightfv(gl.GL_LIGHT0, gl.GL_AMBIENT, [0.2, 0.2, 0.2, 1])

    def update(self, dt):
        """
        Update simulation state.

        Args:
            dt (float): Time step in seconds
        """
        if self.paused:
            return

        # Update particle system with attractor influence if active
        attractor = self.attractor if self.attractor_active else None
        self.particle_system.update(dt, attractor)

    def display(self):
        """Render the scene."""
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        # Set up camera view
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        self.camera.apply()

        # Draw particles
        self.particle_system.draw()

        # Draw emitter if enabled
        if self.show_emitter:
            self.draw_emitter()

        # Draw attractor if enabled
        if self.show_attractor:
            self.attractor.draw()

        # Draw help text if enabled
        if self.show_help:
            self.draw_help_text()

        glut.glutSwapBuffers()

    def draw_emitter(self):
        """Draw the cylindrical emitter as wireframe."""
        gl.glDisable(gl.GL_LIGHTING)
        gl.glColor3f(0.2, 0.7, 0.2)  # Green wireframe
        gl.glPushMatrix()
        glut.glutWireCylinder(
            self.particle_system.emitter_radius,
            self.particle_system.emitter_height,
            20,
            5,
        )
        gl.glPopMatrix()
        gl.glEnable(gl.GL_LIGHTING)

    def draw_help_text(self):
        """Display help text and status information."""
        y = WINDOW_HEIGHT - 20
        lines = [
            "Particle System Simulation",
            f"Particles: {self.particle_count} (up/down arrows to change)",
            f"Trail length: {self.trail_length} (left/right arrows to change)",
            f"Attractor active: {self.attractor_active}",
            "",
            "Controls:",
            "H: Toggle help",
            "P: Pause simulation",
            "E: Toggle emitter visibility",
            "A: Toggle attractor visibility",
            "Space: Toggle attractor activation",
            "R: Reset particles",
            "Up/Down: Increase/decrease particle count",
            "Left/Right: Decrease/increase trail length",
            "Mouse drag: Rotate view",
            "Scroll: Zoom in/out",
        ]

        for line in lines:
            render_text(line, 10, y)
            y -= 20

    def keyboard(self, key, x, y):
        """Handle keyboard input."""
        if key == b"h":
            self.show_help = not self.show_help
        elif key == b"p":
            self.paused = not self.paused
        elif key == b"e":
            self.show_emitter = not self.show_emitter
        elif key == b"a":
            self.show_attractor = not self.show_attractor
        elif key == b" ":
            self.attractor_active = not self.attractor_active
        elif key == b"r":
            self.particle_system.reset()

        glut.glutPostRedisplay()

    def special_keys(self, key, x, y):
        """Handle special key input (arrow keys)."""
        if key == glut.GLUT_KEY_UP:
            # Increase particle count by 50
            self.change_particle_count(50)
        elif key == glut.GLUT_KEY_DOWN:
            # Decrease particle count by 50
            self.change_particle_count(-50)
        elif key == glut.GLUT_KEY_RIGHT:
            # Increase trail length
            self.change_trail_length(1)
        elif key == glut.GLUT_KEY_LEFT:
            # Decrease trail length
            self.change_trail_length(-1)

        glut.glutPostRedisplay()

    def mouse(self, button, state, x, y):
        """Handle mouse button presses."""
        self.camera.handle_mouse_button(button, state, x, y)

    def motion(self, x, y):
        """Handle mouse motion with buttons pressed."""
        self.camera.handle_mouse_motion(x, y)
        glut.glutPostRedisplay()

    def mouse_wheel(self, wheel, direction, x, y):
        """Handle mouse wheel for zoom."""
        self.camera.handle_mouse_wheel(direction)
        glut.glutPostRedisplay()


# Global variables
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
simulation = None
last_time = 0


def display():
    """GLUT display callback."""
    global simulation
    simulation.display()


def reshape(width, height):
    """GLUT reshape callback."""
    global WINDOW_WIDTH, WINDOW_HEIGHT
    WINDOW_WIDTH, WINDOW_HEIGHT = width, height

    gl.glViewport(0, 0, width, height)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    glu.gluPerspective(45, width / height, 0.1, 100.0)


def keyboard(key, x, y):
    """GLUT keyboard callback."""
    global simulation
    simulation.keyboard(key, x, y)


def special_keys(key, x, y):
    """GLUT special key callback."""
    global simulation
    simulation.special_keys(key, x, y)


def mouse(button, state, x, y):
    """GLUT mouse callback."""
    global simulation
    simulation.mouse(button, state, x, y)


def motion(x, y):
    """GLUT motion callback."""
    global simulation
    simulation.motion(x, y)


def idle():
    """GLUT idle callback for animation."""
    global last_time, simulation

    # Calculate time delta
    current_time = glut.glutGet(glut.GLUT_ELAPSED_TIME)
    dt = (current_time - last_time) / 1000.0  # Convert to seconds
    last_time = current_time

    # Cap dt to avoid large time steps
    dt = min(dt, 0.05)

    # Update simulation
    simulation.update(dt)
    glut.glutPostRedisplay()


def mouse_wheel(wheel, direction, x, y):
    """GLUT mouse wheel callback."""
    global simulation
    simulation.mouse_wheel(wheel, direction, x, y)


def main():
    """Initialize GLUT and start the application."""
    global simulation, last_time

    # Initialize GLUT
    glut.glutInit(sys.argv)
    glut.glutInitDisplayMode(glut.GLUT_DOUBLE | glut.GLUT_RGB | glut.GLUT_DEPTH)
    glut.glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glut.glutCreateWindow(b"Particle System Simulation")

    # Create simulation
    simulation = ParticleSimulation()
    simulation.init_gl()

    # Register GLUT callbacks
    glut.glutDisplayFunc(display)
    glut.glutReshapeFunc(reshape)
    glut.glutKeyboardFunc(keyboard)
    glut.glutSpecialFunc(special_keys)
    glut.glutMouseFunc(mouse)
    glut.glutMotionFunc(motion)
    glut.glutIdleFunc(idle)
    glut.glutMouseWheelFunc(mouse_wheel)

    # Initialize time
    last_time = glut.glutGet(glut.GLUT_ELAPSED_TIME)

    # Start main loop
    glut.glutMainLoop()


if __name__ == "__main__":
    main()
