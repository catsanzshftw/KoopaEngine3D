from ursina import *
import time, math

app = Ursina()
window.title = 'SM64-Style Mario Engine'
window.fps_counter.enabled = True

# ---------------------------------------------------
# Mario entity with SM64-inspired physics and moveset
# ---------------------------------------------------
class Mario(Entity):
    def __init__(self, model_path='mario.gltf', **kwargs):
        super().__init__(
            model=model_path,
            texture='mario_texture.png',
            scale=1,
            collider='box',
            **kwargs
        )
        self.velocity = Vec3(0,0,0)
        self.acceleration = 50
        self.max_speed = 8
        self.friction = 10
        self.gravity = 30
        self.jump_speed = 12
        self.grounded = False
        self.jump_count = 0          # track jumps for double / triple jump
        self.camera_offset = Vec3(0,5,-10)

    def update(self):
        dt = time.dt
        # Movement input
        move_input = Vec3(held_keys['d'] - held_keys['a'], 0, held_keys['w'] - held_keys['s'])
        if move_input.length():
            move_dir = move_input.normalized()
            move_dir = move_dir.rotate_y(camera.rotation_y)
            self.velocity.x += move_dir.x * self.acceleration * dt
            self.velocity.z += move_dir.z * self.acceleration * dt
        else:
            self.velocity.x = lerp(self.velocity.x, 0, min(self.friction * dt, 1))
            self.velocity.z = lerp(self.velocity.z, 0, min(self.friction * dt, 1))

        # Clamp speed
        horizontal = Vec3(self.velocity.x, 0, self.velocity.z)
        if horizontal.length() > self.max_speed:
            horizontal = horizontal.normalized() * self.max_speed
            self.velocity.x, self.velocity.z = horizontal.x, horizontal.z

        # Gravity
        if not self.grounded:
            self.velocity.y -= self.gravity * dt

        # Jump logic
        if held_keys['space'] and self.grounded:
            self.velocity.y = self.jump_speed
            self.grounded = False
            self.jump_count = 1
        elif held_keys['space'] and self.jump_count and self.jump_count < 3 and self.velocity.y < self.jump_speed/2:
            # mid-air double / triple jump
            self.velocity.y = self.jump_speed
            self.jump_count += 1

        # Ground pound (Ctrl)
        if held_keys['control'] and not self.grounded and self.velocity.y > -self.jump_speed*1.5:
            self.velocity.y = -self.jump_speed*2   # fast downward speed

        # Move
        self.position += self.velocity * dt

        # Ground check
        hit = raycast(self.world_position + Vec3(0,1,0), Vec3(0,-1,0), distance=1.1, ignore=[self])
        if hit.hit:
            self.world_y = hit.world_point.y + 1
            if not self.grounded:
                # landing
                if self.jump_count > 1:
                    Audio('land_hard.wav').play()   # optional landing sound
            self.grounded = True
            self.jump_count = 0
            self.velocity.y = 0
            normal = hit.world_normal
            slope_dir = Vec3(self.velocity.x, 0, self.velocity.z).project(normal)
            self.velocity.x -= slope_dir.x
            self.velocity.z -= slope_dir.z
        else:
            self.grounded = False

        # Camera follow
        camera.position = lerp(camera.position, self.position + self.camera_offset, 5 * dt)
        camera.look_at(self.position + Vec3(0,1,0))

# ---------------------------------------------------
# Simple collectible coin
# ---------------------------------------------------
class Coin(Entity):
    def __init__(self, **kwargs):
        super().__init__(
            model='sphere',
            scale=.5,
            color=color.yellow,
            rotation_speed=Vec3(0,90,0),
            collider='box',
            **kwargs
        )
    def update(self):
        self.rotation_y += self.rotation_speed.y * time.dt
        if self.intersects(player).hit:
            destroy(self)
            Audio('coin.wav').play()

# ---------------------------------------------------
# World setup
# ---------------------------------------------------
level = Entity()

Entity(model='plane', scale=(50,1,50), texture='white_cube', texture_scale=(50,50), collider='box', color=color.green, parent=level)

for x,z in [(5,5),(10,10),(-5,8)]:
    Entity(model='cube', scale=(4,1,4), position=(x,1,z), collider='box', color=color.brown, parent=level)
    Coin(position=(x,2,z))

DirectionalLight(y=2, rotation=(45,-45,0))
AmbientLight(color=color.rgba(100,100,100,0.1))
Sky()

player = Mario(position=(0,1,0))

app.run()
