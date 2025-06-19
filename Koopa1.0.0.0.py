from ursina import *

class PeachCastle(Entity):
    def __init__(self, position=(0, 0, 0)):
        super().__init__(position=position)
        self.stone_parent = Entity(parent=self)
        self.red_parent = Entity(parent=self)
        
        # Define colors (Nintendo 64 palette)
        self.stone_color = color.rgb(158, 149, 137)
        self.roof_color = color.rgb(173, 47, 43)
        self.wall_color = color.rgb(245, 205, 147)
        self.water_color = color.rgb(58, 108, 191, 180)
        
        self.construct_castle()
        self.finalize_castle()
        
    def construct_castle(self):
        # Main structure
        self.create_base()
        self.create_corner_towers()
        self.create_main_roof()
        self.create_central_tower()
        
        # Entrance features
        self.create_front_entrance()
        self.create_bridge()
        self.create_moat()
        
    def create_base(self):
        # Main keep
        Entity(parent=self.stone_parent, model='cube', scale=(12, 6, 16), 
               color=self.stone_color, y=3, z=1.5)
        
        # Front base extension
        Entity(parent=self.stone_parent, model='cube', scale=(8, 3, 4), 
               color=self.stone_color, y=1.5, z=-7)
        
        # Walls
        wall_height = 2.5
        for i in range(4):
            rotation = i * 90
            position = (10 * math.sin(math.radians(rotation)), wall_height/2, 
                        10 * math.cos(math.radians(rotation)))
            Entity(parent=self.stone_parent, model='cube', 
                   scale=(1, wall_height, 20), rotation_y=rotation,
                   color=self.wall_color, position=position)

    def create_corner_towers(self):
        tower_radius, tower_height = 1.8, 8
        positions = [(-6, 0, -8), (6, 0, -8), (-6, 0, 11), (6, 0, 11)]
        
        for pos in positions:
            # Tower base
            Entity(parent=self.stone_parent, model=Cylinder(6), 
                   scale=(tower_radius, tower_height, tower_radius),
                   color=self.stone_color, position=(pos[0], tower_height/2, pos[2]))
            
            # Tower roof
            Entity(parent=self.red_parent, model=Cone(8), 
                   scale=(tower_radius+0.7, 3, tower_radius+0.7), 
                   color=self.roof_color, 
                   position=(pos[0], tower_height, pos[2]),
                   rotation=(0, 22.5, 0))

    def create_main_roof(self):
        # Main roof (pyramid)
        Entity(parent=self.red_parent, model=Cone(4), 
               scale=(12, 6, 16), color=self.roof_color, 
               position=(0, 9, 1.5), rotation_y=45)
        
        # Roof supports at corners
        for z, x in [(9, -4.5), (9, 4.5), (-3.2, -4.5), (-3.2, 4.5)]:
            Entity(parent=self.stone_parent, model=Cylinder(8), 
                   scale=(0.6, 0.6, 0.6), color=self.stone_color, 
                   position=(x, 6.2, z))

    def create_central_tower(self):
        # Central tower
        tower_pos = (0, 0, -5)
        tower_height = 14
        Entity(parent=self.stone_parent, model=Cylinder(8), 
              scale=(2, tower_height, 2), 
              color=self.stone_color, position=(*tower_pos, tower_height/2))
        
        # Tower roof
        Entity(parent=self.red_parent, model=Cone(8),
              scale=(3, 5, 3), 
              color=self.roof_color, 
              position=(tower_pos[0], tower_height-0.3, tower_pos[1]))

    def create_front_entrance(self):
        # Entrance structure
        Entity(parent=self.stone_parent, model='cube', 
               scale=(3, 4, 2), color=self.stone_color, 
               position=(0, 2, -8.5))
        
        # Entrance arch (cylinder subtracted using rotation)
        for i in range(2):
            rotation = (-90, 0, i * 180)
            Entity(parent=self.stone_parent, model=Cylinder(12, start=-90, radius=2, height=3),
                   scale=(1, 1, 1.1), rotation=rotation, 
                   color=self.stone_color, position=(0, 3, -9.6))

    def create_bridge(self):
        # Bridge base
        Entity(parent=self.stone_parent, model='cube', 
              scale=(3.5, 0.4, 8), color=self.stone_color, 
              position=(0, 0.2, -12))
        
        # Bridge rails
        for x_offset in [-2.1, 2.1]:
            Entity(parent=self.stone_parent, model='cube', 
                   scale=(0.3, 0.8, 8), 
                   color=self.stone_color, 
                   position=(x_offset, 0.5, -12))

    def create_moat(self):
        # Water body
        Entity(parent=self, model='plane', 
               scale=(50, 1, 50), 
               color=self.water_color, 
               y=0.1, double_sided=True,
               texture='water')
        
        # Ground terrain
        Entity(parent=self, model='plane', 
               scale=(50, 0, 50), 
               texture='grass',
               collider='box',
               texture_scale=Vec2(20, 20))

    def finalize_castle(self):
        # Combine all stone parts and red parts separately for performance
        self.stone_parent.combine()
        self.stone_parent.collider = 'mesh'
        self.red_parent.combine()
        
        # Destroy temporary parents
        self.stone_parent.collider = None
        self.stone_parent.enabled = False
        self.red_parent.enabled = False

if __name__ == "__main__":
    app = Ursina()
    window.color = color.sky_blue
    
    # Create castle with optimized combined meshes
    castle = PeachCastle(position=(0, -1, 0))
    
    # Camera controls for inspection
    EditorCamera()
    
    # Add directional light
    DirectionalLight(parent=camera, position=(1, 1, -1), shadows=True)
    
    app.run()
