# b3313_courtyard.py
from ursina import *
import math, random, time

class B3313Courtyard(Entity):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.state = 'peaceful'          # peaceful / windy / crimson
        self._build_yard()
        self._build_hedge_maze()
        self._fx_setup()
        invoke(self.set_state, 'peaceful', delay=0.1)  # default

    # ---------- yard & fountain ----------
    def _build_yard(self):
        # paved ground
        Entity(model='plane', scale=(40,1,40),
               texture='courtyard_atlas.png', texture_scale=(10,10),
               collider='box', parent=self, static=True)

        # perimeter walls
        for dx in (-20,20):
            Entity(model='cube', position=(dx,3,0), scale=(1,6,40),
                   texture='courtyard_atlas.png', collider='box',
                   parent=self, static=True)
        for dz in (-20,20):
            Entity(model='cube', position=(0,3,dz), scale=(40,6,1),
                   texture='courtyard_atlas.png', collider='box',
                   parent=self, static=True)

        # central fountain base
        self.fountain = Entity(model='cylinder', position=(0,0.1,0),
                               scale=(6,1,6), texture='courtyard_atlas.png',
                               collider='mesh', parent=self)

        # animated water surface (peaceful only)
        self.water = Entity(model='circle', color=color.azure*0.7,
                            position=(0,0.25,0), scale=5.9, double_sided=True,
                            parent=self)

    # ---------- hedge maze ----------
    def _build_hedge_maze(self):
        self.maze_root = Entity(parent=self, y=0)
        start = Vec3(-12,0,10)
        cell = 4
        layout = [
            "##########",
            "#S   #   #",
            "# ## # # #",
            "#    # #E#",
            "##########",
        ]
        for r,row in enumerate(layout):
            for c,ch in enumerate(row):
                if ch == '#':
                    Entity(model='cube', texture='courtyard_atlas.png',
                           color=color.rgb(40,120,40),
                           position=start + Vec3(c*cell,1,r*cell),
                           scale=(cell,2,cell), collider='box',
                           parent=self.maze_root, static=True)
                 # optional coin spawn points
                  for _ in range(8):
             x = random.uniform(-10,10); z = random.uniform(12,26)
             # Coin(position=(x,0.5,z), parent=self)  # Coin class not defined

    # ---------- ambience controller ----------
    def _fx_setup(self):
        self.dir_light = DirectionalLight(parent=self, rotation=(50,-45,0))
        self.amb = AmbientLight(parent=self, color=color.rgba(80,80,80,0.25))
        self.sky = Sky(texture='sky_default')

    def set_state(self, new_state:str):
        self.state = new_state
        # PEACEFUL -------------------------------------------------------------------
        if new_state == 'peaceful':
            self.water.enabled = True
            self.fountain.texture_scale = (1,1)
            self.sky.texture = 'sky_default'
            self.amb.color = color.rgba(120,120,120,0.3)
        # WINDY ----------------------------------------------------------------------
        elif new_state == 'windy':
            self.water.enabled = False
            self.fountain.texture_scale = (2,2)  # shows plaque texture
            self.sky.texture = 'sky_overcast'
            self.amb.color = color.rgba(180,180,180,0.4)
        # CRIMSON --------------------------------------------------------------------
        elif new_state == 'crimson':
            self.water.enabled = False
            self.fountain.color = color.rgb(80,0,0)
            self.sky.texture = 'sky_black'
            self.amb.color = color.rgba(10,0,0,0.6)

    # press "T" to cycle states for testing
    def input(self,key):
        if key=='t':
            nxt = {'peaceful':'windy','windy':'crimson','crimson':'peaceful'}
            self.set_state(nxt[self.state])

# ---------- demo ----------
if __name__ == '__main__':
    from mario_engine import Mario  # your existing player
    app = Ursina(title='B3313 Courtyard Demo')
    courtyard = B3313Courtyard()
    player = Mario(position=(0,1,18))
    app.run()
