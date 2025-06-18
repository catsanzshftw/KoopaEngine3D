#
# Ursina 3D Courtyard Demo
#
# This Python script is a recreation of the provided three.js web demo,
# built using the Ursina game engine.
#
# To run this code:
# 1. Make sure you have Python installed.
# 2. Install the Ursina engine and the Pillow library:
#    pip install ursina
#    pip install Pillow
# 3. Save this code as a Python file (e.g., courtyard_demo.py) and run it.
#

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from PIL import Image, ImageDraw # Used for procedural texture generation

# --- WEATHER SYSTEM SETUP ---
# We define the different weather states with their corresponding color values.
# Ursina's color system is used (0-255 for RGB, 0-1 for alpha).
weather_states = {
    'Peaceful': {
        'sky_color': color.rgb(25, 30, 40),
        'sun_color': color.rgb(255, 255, 255),
        'ambient_color': color.rgba(64, 64, 80, 128),
        'particles_visible': False
    },
    'Windy': {
        'sky_color': color.rgb(48, 53, 64),
        'sun_color': color.rgb(204, 204, 204),
        'ambient_color': color.rgba(80, 80, 96, 128),
        'particles_visible': True
    },
    'Crimson': {
        'sky_color': color.rgb(80, 32, 16),
        'sun_color': color.rgb(255, 96, 64),
        'ambient_color': color.rgba(128, 48, 32, 128),
        'particles_visible': False
    }
}
# We need to store the names to cycle through them
state_names = list(weather_states.keys())
current_weather_index = 0

# --- PROCEDURAL TEXTURE GENERATION ---
# These functions recreate the canvas-based textures from the JavaScript code
# using the Python Imaging Library (Pillow).

def create_checkerboard_texture():
    """Generates a green checkerboard texture like in the original demo."""
    size = 512
    img = Image.new('RGB', (size, size))
    draw = ImageDraw.Draw(img)
    
    # Colors from the original JS code
    dark_green = '#5a693a'
    light_green = '#6b7f43'
    
    draw.rectangle([0, 0, size, size], fill=dark_green)
    
    tile_size = 16
    num_tiles = size // tile_size
    for i in range(num_tiles):
        for j in range(num_tiles):
            if (i + j) % 2 == 0:
                x0 = i * tile_size
                y0 = j * tile_size
                x1 = x0 + tile_size
                y1 = y0 + tile_size
                draw.rectangle([x0, y0, x1, y1], fill=light_green)
                
    return Texture(img)

def create_brick_texture():
    """Generates a grey brick texture like in the original demo."""
    size = 512
    img = Image.new('RGB', (size, size))
    draw = ImageDraw.Draw(img)
    
    # Colors and dimensions from the original JS code
    mortar_color = '#5c5c5c'
    brick_color = '#8c8c8c'
    brick_width = 60
    brick_height = 28
    mortar_gap = 4
    
    draw.rectangle([0, 0, size, size], fill=mortar_color)
    
    row_height = brick_height + mortar_gap
    num_rows = (size // row_height) + 1
    col_width = brick_width + mortar_gap
    num_cols = (size // col_width) + 1
    
    for y_idx in range(num_rows):
        for x_idx in range(num_cols):
            offset_x = 0
            # Every other row is offset for a running bond pattern
            if y_idx % 2 != 0:
                offset_x = -brick_width // 2
            
            x = (x_idx * col_width) + offset_x
            y = y_idx * row_height
            
            draw.rectangle([x, y, x + brick_width, y + brick_height], fill=brick_color)

    return Texture(img)

# --- APPLICATION INITIALIZATION ---
app = Ursina(
    title='Ursina Courtyard Demo',
    borderless=False,
    fullscreen=False,
    size=(600, 400), # Set the fixed window size as requested
    development_mode=False
)
window.exit_button.visible = True
window.cog_button.visible = False # Hides the settings cog

# --- SCENE SETUP ---

# Ground
# A simple entity with a plane model, scaled up, with the checkerboard texture.
# A box collider is added so the player can walk on it.
ground_texture = create_checkerboard_texture()
ground = Entity(
    model='plane',
    scale=(200, 1, 200),
    texture=ground_texture,
    texture_scale=(50, 50),
    collider='box'
)

# Central Courtyard Structure
# We load the brick texture once and apply it to all structure parts.
pillar_texture = create_brick_texture()

# Central base
Entity(model='cube', scale=(10, 5, 10), position=(0, 2.5, 0), texture=pillar_texture, collider='box')

# Four pillars, positioned in a circle using trigonometry
for i in range(4):
    angle = (i / 4) * math.pi * 2
    x = math.cos(angle) * 15
    z = math.sin(angle) * 15
    Entity(model='cube', scale=(2, 12, 2), position=(x, 6, z), texture=pillar_texture, collider='box')

# Player
# Ursina's FirstPersonController handles all movement, jumping, and gravity.
player = FirstPersonController(
    position=(0, 5, 10),
    speed=8,
    jump_height=3,
    gravity=1.0 # Ursina's gravity is a downward multiplier
)

# Particle System for "Windy" state
# We create a parent entity for the particles and then create a number of small
# quad entities that will be moved in the update loop.
wind_parent = Entity()
particles = []
for _ in range(200):
    p = Entity(
        parent=wind_parent,
        model='quad',
        scale=0.1,
        color=color.light_gray,
        position=(
            random.uniform(-100, 100),
            random.uniform(0, 50),
            random.uniform(-100, 100)
        )
    )
    particles.append(p)
wind_parent.visible = False # Start with particles hidden

# Lighting
# We set up a directional light for the sun and control ambient light via a color property.
sun = DirectionalLight(y=50, z=25, shadows=True)
AmbientLight(color=color.rgba(64, 64, 80, 128)) # Initial ambient color

# --- UI SETUP ---
# Create Text entities to display information on screen.
# `window.top_left` and `window.top_right` are used for easy placement.
weather_text = Text(
    text='Weather: Peaceful',
    origin=(-.5, .5),
    position=window.top_left + (.02, -.02)
)
instructions_text = Text(
    text='T = Cycle Weather | F = Toggle FPS',
    origin=(-.5, .5),
    position=window.top_left + (.02, -.05)
)
window.fps_counter.enabled = True # Start with FPS counter visible

# --- MAIN LOGIC (INPUT AND UPDATE LOOPS) ---

def cycle_weather():
    """Cycles to the next weather state and updates the UI."""
    global current_weather_index
    current_weather_index = (current_weather_index + 1) % len(state_names)
    state_name = state_names[current_weather_index]
    weather_text.text = f"Weather: {state_name}"
    
def input(key):
    """Handles key presses."""
    if key == 't':
        cycle_weather()
    if key == 'f':
        window.fps_counter.enabled = not window.fps_counter.enabled

def update():
    """This function is called every frame."""
    # 1. Smoothly transition weather colors
    target_state = weather_states[state_names[current_weather_index]]
    transition_speed = time.dt * 1.0
    
    # Lerp (linear interpolate) colors for a smooth transition effect
    window.color = lerp(window.color, target_state['sky_color'], transition_speed)
    sun.color = lerp(sun.color, target_state['sun_color'], transition_speed)
    
    # 2. Update particle system for "Windy" weather
    wind_parent.visible = target_state['particles_visible']
    if wind_parent.visible:
        for p in particles:
            p.x -= time.dt * 15 # Move particles
            if p.x < -100: # Loop particles that go off-screen
                p.x = 100

# Start the application
app.run()
