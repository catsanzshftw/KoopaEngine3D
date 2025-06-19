from ursina import *
import random

app = Ursina()

# Create Mario-like player
class Player(Entity):
    def __init__(self):
        super().__init__(
            model='cube',
            texture='white_cube',
            color=color.red,
            scale=(1, 1.8, 1),
            position=(0, 2, 0),
            collider='box'
        )
        self.speed = 5
        self.jump_height = 4
        self.gravity = 1
        self.velocity_y = 0
        self.grounded = False
        self.can_jump = True  # Flag to control jumping

    def update(self):
        # Camera-relative movement with collision detection
        cam_forward = camera.forward
        cam_forward.y = 0
        cam_forward = cam_forward.normalized()
        
        cam_right = camera.right
        cam_right.y = 0
        cam_right = cam_right.normalized()
        
        movement = Vec3(0, 0, 0)
        if held_keys['w']: movement += cam_forward
        if held_keys['s']: movement -= cam_forward
        if held_keys['d']: movement += cam_right
        if held_keys['a']: movement -= cam_right
        
        # Normalize movement vector to prevent faster diagonal movement
        if movement.length() > 0:
            movement = movement.normalized()
            
        # Check horizontal collisions
        move_distance = movement.length() * self.speed * time.dt
        if move_distance > 0:
            hit = raycast(self.position, movement, distance=move_distance + 0.1)
            if not hit.hit:
                self.position += movement * self.speed * time.dt
                
        # Apply gravity
        if not self.grounded:
            self.velocity_y -= self.gravity * time.dt
        
        # Apply vertical movement
        self.y += self.velocity_y * time.dt
        
        # Ground check
        ray = raycast(self.position + (0, -0.9, 0), (0, -1, 0), distance=0.1)
        self.grounded = ray.hit
        if self.grounded:
            self.velocity_y = 0
            self.can_jump = True  # Reset jump ability when grounded
        
        # Keep player above ground
        if self.y < -10:
            self.position = (0, 10, 0)
            self.velocity_y = 0

    def input(self, key):
        if key == 'space' and self.grounded and self.can_jump:
            self.velocity_y = self.jump_height
            self.grounded = False
            self.can_jump = False  # Prevent multiple jumps

# Create Mario 64-style environment
def create_map():
    # Ground
    Entity(
        model='plane',
        texture='grass',
        scale=(50, 1, 50),
        position=(0, -0.5, 0),
        collider='box'
    )
    
    # Start platform
    Entity(
        model='cube',
        texture='white_cube',
        scale=(10, 1, 10),
        position=(0, 0, 0),
        collider='box'
    )
    
    # Platforms
    positions = [
        (5, 2, 8), (10, 4, 15), (15, 6, 5),
        (-5, 3, 10), (-10, 5, -5), (0, 8, -10)
    ]
    for i, pos in enumerate(positions):
        Entity(
            model='cube',
            texture='brick' if i % 2 == 0 else 'white_cube',
            scale=(4, 0.5, 4),
            position=pos,
            collider='box'
        )
    
    # Question blocks
    for pos in [(3, 4, 3), (-3, 5, -3), (0, 10, 0)]:
        Entity(
            model='cube',
            texture='yellow_cube',
            scale=(1.5, 1.5, 1.5),
            position=pos,
            collider='box'
        )
    
    # Coins
    for i in range(20):
        model = 'sphere' if i % 2 == 0 else 'quad'
        scale = 0.5 if model == 'sphere' else (0.5, 0.5, 0.01)
        Entity(
            model=model,
            color=color.gold,
            scale=scale,
            position=(random.uniform(-15, 15),
                      random.uniform(2, 10),
                      random.uniform(-15, 15)),
            collider='sphere' if model == 'sphere' else 'box'
        )
    
    # Castle-like structure
    Entity(
        model='cube',
        texture='brick',
        scale=(8, 6, 8),
        position=(20, 3, 0),
        collider='box'
    )
    Entity(
        model='cone',
        color=color.red,
        scale=(1.5, 3, 1.5),
        position=(20, 9, 0)
    )
    
    # Trees
    for i in range(10):
        pos = (random.uniform(-20, 20), 0, random.uniform(-20, 20))
        Entity(
            model='cylinder',
            texture='grass',
            scale=(0.5, 3, 0.5),
            position=pos,
            collider='box'
        )
        Entity(
            model='sphere',
            texture='grass',
            color=color.green,
            scale=(2, 2, 2),
            position=(pos[0], 3, pos[2])
        )

# Create map and player
create_map()
player = Player()

# Camera setup - Third person camera
camera.position = (0, 15, -20)
camera.rotation_x = 30
camera.fov = 80

# Function to update camera position to follow player
def update():
    camera.position = player.position + (0, 15, -20)
    camera.look_at(player.position + (0, 5, 5))

# Skybox
Sky(texture='sky_sunset')

# Add a simple title
Text("Mario 64 Test Map", origin=(0, 0), scale=2, position=(0, 0.4, 0))

# Add instructions
instructions = Text(
    "Controls: WASD to move\nSpace to jump\nMouse to look around",
    origin=(0, 0),
    scale=1,
    position=(0, -0.4, 0)
)

app.run()
