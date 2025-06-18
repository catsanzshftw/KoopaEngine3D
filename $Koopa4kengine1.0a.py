from ursina import *

app = Ursina()

# --- Castle -------------------------------------------------
castle = Entity(
    model='castle.glb',           # lives in assets/
    texture='castle_atlas.png',   # optional – bundled in .glb by default
    collider='mesh',              # triangle collider for precise walls
    static=True,                  # bakes it into one GPU call
    scale=1, position=(0,0,0)
)

# Move existing basics
# load_b3313_outside()              # keep your rolling hills - function not defined
# player = Mario(position=(0,2,30))  # Mario class not defined

Sky(texture='sky_sunset')
DirectionalLight(rotation=(45,-45,0), shadows=True)

app.run()
