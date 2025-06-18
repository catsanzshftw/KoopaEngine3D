"""
Ursina Engine Courtyard Demo
Fixed and refined according to modern Python practices
"""

# Standard library imports
import math
from pathlib import Path
from typing import Final, Literal, Tuple

# Third-party imports
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController

# Constants
VALID_STATES: Final[Tuple[Literal["peaceful", "windy", "crimson"], ...]] = (
    "peaceful",
    "windy",
    "crimson",
)
BACKGROUND_COLOR = color.rgba(25, 30, 40, 255)
MOUSE_SENSITIVITY = (40, 40)
FOG_DENSITY = 0.05
FPS_TOGGLE_KEY = "tab"

def _rgba_f32(r: int, g: int, b: int, a: int = 255) -> Vec4:
    """Convert 0-255 RGBA values to normalized 0.0-1.0 range."""
    return Vec4(r / 255, g / 255, b / 255, a / 255)

def safe_texture(path_str: str) -> Texture:
    """
    Load texture with fallback validation. Return checker pattern if:
    1. Path doesn't exist
    2. Path is directory
    3. File loading fails
    """
    tex_path = Path(path_str)
    if not tex_path.exists() or not tex_path.is_file():
        return load_texture("white_cube")
    
    try:
        return load_texture(str(tex_path))
    except Exception:
        return load_texture("white_cube")

class WeatherCycle(Entity):
    """Dynamic weather state manager with smooth transitions"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state = "peaceful"
        self.transition_speed = 0.25
        
    def shift(self, target_state: str) -> None:
        """Transition to new weather state if valid"""
        if target_state in VALID_STATES:
            self.state = target_state

class EnhancedPlayer(FirstPersonController):
    """Extended player controller with quality-of-life improvements"""
    def __init__(self, **kwargs):
        super().__init__(
            mouse_sensitivity=MOUSE_SENSITIVITY,
            jump_height=2.5,
            **kwargs
        )
        self.fps_counter_visible = True
        
    def input(self, key: str) -> None:
        """Handle extended input events"""
        super().input(key)
        if key == FPS_TOGGLE_KEY:
            self.fps_counter_visible = not self.fps_counter_visible
            application.fps_counter.enabled = self.fps_counter_visible

class CourtyardScene(Entity):
    """Main environment container with dynamic elements"""
    def __init__(self, weather: WeatherCycle, **kwargs):
        super().__init__(**kwargs)
        self.weather = weather
        
        # Environment setup
        self.sky = Sky(texture="sky_sunset")
        self.ground = Entity(
            model="plane",
            scale=(100, 1, 100),
            texture="grass",
            texture_scale=(16, 16),
            shader=lit_with_shadows_shader
        )
        
        # Lighting setup
        self.directional_light = DirectionalLight(
            shadows=True,
            rotation=(45, -30, 0)
        )
        self.ambient_light = AmbientLight(color=_rgba_f32(50, 50, 60))
        
        # Weather-sensitive elements
        # self.wind_particles = ParticleSystem(  # ParticleSystem not available in Ursina
        #     enabled=(self.weather.state == "windy")
        # )
        
    def update(self) -> None:
        """Update scene based on weather state"""
        self.wind_particles.enabled = (self.weather.state == "windy")
        
        # Apply fog effects
        if hasattr(scene, "fog_color") and hasattr(scene, "fog_density"):
            scene.fog_density = FOG_DENSITY
            scene.fog_color = BACKGROUND_COLOR

if __name__ == "__main__":
    # Engine configuration
    app = Ursina(
        title="Courtyard Demo",
        fullscreen=False,
        development_mode=True
    )
    
    # Apply global settings
    window.color = BACKGROUND_COLOR
    mouse.visible = False
    scene.fog_color = color.rgb(25, 30, 40)
    scene.fog_density = FOG_DENSITY
    
    # Create game objects
    weather_system = WeatherCycle()
    player = EnhancedPlayer(position=(0, 2, 0))
    courtyard = CourtyardScene(weather=weather_system)
    
    # Debug controls
    def toggle_weather() -> None:
        """Cycle through weather states for testing"""
        current_idx = VALID_STATES.index(weather_system.state)
        next_idx = (current_idx + 1) % len(VALID_STATES)
        weather_system.shift(VALID_STATES[next_idx])
        print(f"Weather shifted to: {weather_system.state}")
    
    # Set up input hooks
    weather_system.shift("windy")
    invoke(toggle_weather, delay=10, loop=True)
    
    # Start main loop
    app.run()
