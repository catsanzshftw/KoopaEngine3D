import pygame
import math
import random
import sys
from collections import namedtuple
from enum import Enum, auto

# Initialize pygame
pygame.init()
WIDTH, HEIGHT = 800, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paper Mario: Thousand-Year Door Engine")

# Constants
GROUND_LEVEL = HEIGHT - 60
CAMERA_SMOOTHNESS = 0.1
GRAVITY = 0.7
JUMP_POWER = 14
FPS = 60

# Named tuples for better structure
Color = namedtuple('Color', ['r', 'g', 'b'])
Point = namedtuple('Point', ['x', 'y'])
Size = namedtuple('Size', ['width', 'height'])

# Color definitions
BACKGROUND = Color(100, 160, 255)
GROUND_COLOR = Color(136, 84, 50)
GREEN = Color(60, 160, 55)
RED = Color(222, 55, 55)
YELLOW = Color(255, 220, 70)
BLUE = Color(70, 150, 255)
BROWN = Color(139, 69, 19)
LIGHT_BROWN = Color(180, 140, 80)
WHITE = Color(255, 255, 255)
BLACK = Color(20, 20, 20)
KOOPA_GREEN = Color(60, 150, 60)
KOOPA_SHELL = Color(130, 190, 70)
KOOPA_DARK = Color(40, 110, 40)
BANDANA_BLUE = Color(40, 110, 220)
PURPLE = Color(160, 80, 210)
ORANGE = Color(255, 145, 30)
PAPER_YELLOW = Color(250, 240, 180)
MENU_BG = Color(80, 140, 220)
MENU_HIGHLIGHT = Color(120, 180, 255)

# Game states
class GameState(Enum):
    MENU = auto()
    BOOT = auto()
    GAMEPLAY = auto()
    GAME_OVER = auto()

class VectorFont:
    @staticmethod
    def render_text(surface, text, x, y, size, color, outline_color=BLACK, outline=2):
        char_width = size * 0.6
        spacing = size * 0.1
        
        for i, char in enumerate(text):
            char_x = x + i * (char_width + spacing)
            VectorFont.draw_char(surface, char, char_x, y, size, color, outline_color, outline)
    
    @staticmethod
    def draw_char(surface, char, x, y, size, color, outline_color, outline):
        scale = size / 30
        char_def = CHAR_DEFINITIONS.get(char, CHAR_DEFINITIONS['?'])
        
        for line in char_def:
            scaled_line = []
            for point in line:
                scaled_point = (x + point[0] * scale, y + point[1] * scale)
                scaled_line.append(scaled_point)
            
            if len(scaled_line) > 1:
                pygame.draw.lines(surface, outline_color, False, scaled_line, outline + 2)
            pygame.draw.lines(surface, color, False, scaled_line, outline)

# Character definitions
CHAR_DEFINITIONS = {
    'A': [[(0, 30), (15, 0)], [(15, 0), (30, 30)], [(5, 20), (25, 20)]],
    'B': [[(0, 0), (0, 30)], [(0, 0), (20, 0), (25, 5), (25, 10), (20, 15), (0, 15)], 
          [(0, 15), (20, 15), (25, 20), (25, 25), (20, 30), (0, 30)]],
    'C': [[(25, 0), (5, 0), (0, 5), (0, 25), (5, 30), (25, 30)]],
    'D': [[(0, 0), (0, 30)], [(0, 0), (20, 0), (30, 10), (30, 20), (20, 30), (0, 30)]],
    'E': [[(0, 0), (0, 30)], [(0, 0), (25, 0)], [(0, 15), (20, 15)], [(0, 30), (25, 30)]],
    'F': [[(0, 0), (0, 30)], [(0, 0), (25, 0)], [(0, 15), (20, 15)]],
    'G': [[(25, 0), (5, 0), (0, 5), (0, 25), (5, 30), (25, 30), (30, 25)], 
          [(30, 25), (20, 25), (20, 15)]],
    'H': [[(0, 0), (0, 30)], [(30, 0), (30, 30)], [(0, 15), (30, 15)]],
    'I': [[(0, 0), (30, 0)], [(15, 0), (15, 30)], [(0, 30), (30, 30)]],
    'J': [[(15, 0), (30, 0)], [(30, 0), (30, 20), (25, 30), (15, 30), (10, 25), (10, 20)]],
    'K': [[(0, 0), (0, 30)], [(0, 15), (30, 0)], [(0, 15), (30, 30)]],
    'L': [[(0, 0), (0, 30)], [(0, 30), (25, 30)]],
    'M': [[(0, 30), (0, 0), (15, 15), (30, 0), (30, 30)]],
    'N': [[(0, 30), (0, 0), (30, 30), (30, 0)]],
    'O': [[(0, 0), (0, 30), (30, 30), (30, 0), (0, 0)]],
    'P': [[(0, 0), (0, 30)], [(0, 0), (20, 0), (30, 10), (30, 15), (20, 30), (0, 30)]],
    'Q': [[(0, 0), (0, 30), (30, 30), (30, 0), (0, 0)], [(15, 15), (30, 30)]],
    'R': [[(0, 0), (0, 30)], [(0, 0), (20, 0), (30, 10), (30, 15), (20, 30), (0, 30)], 
          [(15, 15), (30, 30)]],
    'S': [[(25, 0), (5, 0), (0, 5), (0, 15), (5, 15), (25, 15), (30, 20), (30, 25), (25, 30), (5, 30)]],
    'T': [[(0, 0), (30, 0)], [(15, 0), (15, 30)]],
    'U': [[(0, 0), (0, 25), (5, 30), (25, 30), (30, 25), (30, 0)]],
    'V': [[(0, 0), (15, 30), (30, 0)]],
    'W': [[(0, 0), (0, 30), (15, 15), (30, 30), (30, 0)]],
    'X': [[(0, 0), (30, 30)], [(30, 0), (0, 30)]],
    'Y': [[(0, 0), (15, 15), (30, 0)], [(15, 15), (15, 30)]],
    'Z': [[(0, 0), (30, 0)], [(30, 0), (0, 30)], [(0, 30), (30, 30)]],
    ' ': [],
    '!': [[(15, 0), (15, 20)], [(15, 25), (15, 30)]],
    '?': [[(5, 0), (25, 0), (30, 5), (30, 15), (20, 25), (15, 25)], [(15, 30), (15, 30)]],
    '/': [[(30, 0), (0, 30)]],
    ':': [[(15, 10), (15, 10)], [(15, 20), (15, 20)]],
    '.': [[(15, 25), (15, 25)]],
    ',': [[(15, 25), (10, 30)]],
    "'": [[(15, 0), (15, 10)]],
    '"': [[(10, 0), (10, 10)], [(20, 0), (20, 10)]],
    '(': [[(20, 0), (10, 15), (20, 30)]],
    ')': [[(10, 0), (20, 15), (10, 30)]],
    '[': [[(20, 0), (10, 0)], [(10, 0), (10, 30)], [(10, 30), (20, 30)]],
    ']': [[(10, 0), (20, 0)], [(20, 0), (20, 30)], [(20, 30), (10, 30)]],
    '-': [[(5, 15), (25, 15)]],
    '?': [[(5, 0), (25, 0), (30, 5), (30, 15), (20, 25), (15, 25)], [(15, 30), (15, 30)]]
}

class Koops:
    def __init__(self, x, y):
        self.position = Point(x, y)
        self.size = Size(40, 50)
        self.walking_speed = 4
        self.running_speed = 6
        self.speed = self.walking_speed
        self.velocity_y = 0
        self.direction = 1
        self.leg_offset = 0
        self.head_bob = 0
        self.bandana_offset = 0
        self.is_jumping = False
        self.is_grounded = False
        self.crouching = False
        self.running = False
        self.hit_points = 3
        self.invincible = 0
        self.closing_eyes = 0
        
    def update(self, platforms):
        time = pygame.time.get_ticks() * 0.01
        self.leg_offset = math.sin(time) * 4
        self.head_bob = math.sin(time * 3) * 1
        self.bandana_offset = math.sin(time * 2.5) * 3
        
        self.velocity_y += GRAVITY
        self.position = Point(self.position.x, self.position.y + self.velocity_y)
        
        if self.invincible > 0:
            self.invincible -= 1
        
        if self.closing_eyes > 0:
            self.closing_eyes -= 1
        elif random.random() < 0.005:
            self.closing_eyes = 7
            
        self.is_grounded = False
        if self.position.y >= GROUND_LEVEL - self.size.height:
            self.position = Point(self.position.x, GROUND_LEVEL - self.size.height)
            self.velocity_y = 0
            self.is_grounded = True
            self.is_jumping = False
            
        for platform in platforms:
            if (self.position.x + self.size.width > platform.position.x and 
                self.position.x < platform.position.x + platform.size.width and
                self.position.y + self.size.height > platform.position.y and
                self.position.y + self.size.height < platform.position.y + 20 and
                self.velocity_y > 0):
                self.position = Point(self.position.x, platform.position.y - self.size.height)
                self.velocity_y = 0
                self.is_grounded = True
                self.is_jumping = False
                
    def move(self, dx, platforms):
        if self.crouching:
            return
            
        self.speed = self.running_speed if self.running else self.walking_speed
        new_x = self.position.x + dx * self.speed
        new_x = max(0, min(WIDTH - self.size.width, new_x))
        
        if dx > 0:
            self.direction = 1
        elif dx < 0:
            self.direction = -1
            
        for platform in platforms:
            if (new_x + self.size.width > platform.position.x and 
                new_x < platform.position.x + platform.size.width and
                self.position.y + self.size.height > platform.position.y and
                self.position.y < platform.position.y + platform.size.height):
                if dx > 0:
                    new_x = platform.position.x - self.size.width
                elif dx < 0:
                    new_x = platform.position.x + platform.size.width
        
        self.position = Point(new_x, self.position.y)
                    
    def jump(self):
        if self.is_grounded and not self.is_jumping:
            self.velocity_y = -JUMP_POWER
            self.is_jumping = True
            self.is_grounded = False
            
    def crouch(self, crouch):
        self.crouching = crouch
        self.size = Size(self.size.width, 35 if crouch else 50)
    
    def run(self, run):
        self.running = run
    
    def damage(self):
        if self.invincible == 0:
            self.hit_points -= 1
            self.invincible = 30
            
    def draw(self, surface):
        # Draw shadow
        pygame.draw.ellipse(surface, (*BLACK, 100), 
            (self.position.x - 10, self.position.y + self.size.height - 5, 40, 10))
        
        # Draw shell
        shell_rect = (self.position.x - 15, self.position.y - 25, self.size.width, 25)
        pygame.draw.ellipse(surface, KOOPA_SHELL, shell_rect)
        pygame.draw.ellipse(surface, BLACK, shell_rect, 2)
        
        # Shell pattern
        nubs = [
            (self.position.x, self.position.y - 10), 
            (self.position.x - 10, self.position.y - 5),
            (self.position.x + 10, self.position.y - 5),
            (self.position.x, self.position.y)
        ]
        for pos in nubs:
            pygame.draw.circle(surface, (150, 175, 60), pos, 4)
            pygame.draw.circle(surface, BLACK, pos, 4, 1)
        
        # Draw head
        head_y = self.position.y - 40 + self.head_bob
        head_x = self.position.x
        
        # Draw bandana
        bandana_points = [
            (head_x - 20, head_y - self.bandana_offset - 5),
            (head_x - 15, head_y - self.bandana_offset - 8),
            (head_x + 15, head_y - self.bandana_offset - 8),
            (head_x + 20, head_y - self.bandana_offset - 5)
        ]
        pygame.draw.polygon(surface, BANDANA_BLUE, bandana_points)
        pygame.draw.polygon(surface, BLACK, bandana_points, 2)
        
        # Bandana knot
        pygame.draw.circle(surface, (30, 80, 200), 
                          (head_x, head_y - self.bandana_offset - 8), 4)
        
        # Head shape
        head_rect = (head_x - 15, head_y, 30, 18)
        pygame.draw.ellipse(surface, KOOPA_GREEN, head_rect)
        pygame.draw.ellipse(surface, KOOPA_DARK, head_rect, 2)
        
        # Eyes
        eye_x = head_x - 5 if self.direction == -1 else head_x + 5
        eye_x += self.direction
        
        eye_open = self.closing_eyes < 4
        eye_height = 10 if eye_open else 2
        pygame.draw.ellipse(surface, WHITE, 
                           (eye_x - 5, head_y + 5, 10, eye_height))
        if eye_open:
            pupil_size = 4 if self.invincible % 6 >= 3 else 5
            pygame.draw.circle(surface, BLACK, 
                              (eye_x, head_y + 8), pupil_size)
        
        # Mouth expression
        if self.invincible > 0 and self.invincible % 10 > 4:
            pygame.draw.arc(surface, (120, 40, 40), 
                           (head_x - 12, head_y - 1, 24, 12), 
                           math.pi, 2 * math.pi, 2)
        else:
            pygame.draw.arc(surface, KOOPA_DARK, 
                           (head_x - 8, head_y + 5, 16, 10), 
                           0, math.pi, 2)
        
        # Legs
        for i, side in enumerate([-1, 1]):
            leg_x = self.position.x + side * 7
            leg_y = self.position.y - 15 + self.leg_offset * (1 if i == 0 else -1)
            pygame.draw.ellipse(surface, KOOPA_DARK, 
                              (leg_x - 5, leg_y, 10, 12))
            
        # Health meter
        for i in range(3):
            fill = i < self.hit_points
            hp_x = self.position.x + i * 15
            hp_y = self.position.y - 55
            
            pygame.draw.circle(surface, RED if fill else (120, 120, 120), 
                              (hp_x - 3, hp_y - 2), 4)
            pygame.draw.circle(surface, RED if fill else (120, 120, 120), 
                              (hp_x + 3, hp_y - 2), 4)
            pygame.draw.polygon(surface, RED if fill else (120, 120, 120), [
                (hp_x - 5, hp_y - 1),
                (hp_x + 5, hp_y - 1),
                (hp_x, hp_y + 5)
            ])
            
            pygame.draw.line(surface, BLACK, (hp_x - 3, hp_y - 2), (hp_x - 5, hp_y - 1), 1)
            pygame.draw.line(surface, BLACK, (hp_x - 3, hp_y - 2), (hp_x, hp_y + 5), 1)
            pygame.draw.line(surface, BLACK, (hp_x + 3, hp_y - 2), (hp_x + 5, hp_y - 1), 1)
            pygame.draw.line(surface, BLACK, (hp_x + 3, hp_y - 2), (hp_x, hp_y + 5), 1)

class Goomba:
    def __init__(self, x, y, walk_range=100):
        self.position = Point(x, y)
        self.size = Size(30, 20)
        self.speed = 1.5
        self.direction = -1
        self.walk_range = walk_range
        self.start_x = x
        self.squish = 0
        self.animation_offset = 0
        self.crushed = False
        
    def update(self):
        self.animation_offset = math.sin(pygame.time.get_ticks() * 0.03) * 2
        
        if not self.crushed:
            new_x = self.position.x + self.speed * self.direction
            if abs(new_x - self.start_x) > self.walk_range:
                self.direction *= -1
                new_x = self.position.x + self.speed * self.direction
                
            self.position = Point(new_x, GROUND_LEVEL - self.size.height)
                
    def draw(self, surface, camera_offset):
        if self.crushed:
            pygame.draw.ellipse(surface, BROWN,
                               (self.position.x - camera_offset, self.position.y + 5, 
                                self.size.width, 8))
            pygame.draw.ellipse(surface, BLACK, 
                               (self.position.x - camera_offset, self.position.y + 5, 
                                self.size.width, 8), 1)
            return
        
        pygame.draw.ellipse(surface, (*BLACK, 100), 
                          (self.position.x - 10 - camera_offset, self.position.y + self.size.height - 3, 
                           30, 8))
        
        body_rect = (self.position.x - camera_offset, self.position.y + self.animation_offset, 
                    self.size.width, self.size.height - (self.squish * 10))
        pygame.draw.ellipse(surface, BROWN, body_rect)
        pygame.draw.ellipse(surface, BLACK, body_rect, 1)
        
        pygame.draw.ellipse(surface, BLACK, 
                          (self.position.x - camera_offset + 5, self.position.y + self.size.height - 5, 
                           6, 5))
        pygame.draw.ellipse(surface, BLACK, 
                          (self.position.x - camera_offset + 19, self.position.y + self.size.height - 5, 
                           6, 5))
        
        eye_pos = [
            (self.position.x - camera_offset + 8, self.position.y + 7),
            (self.position.x - camera_offset + 22, self.position.y + 7)
        ]
        for pos in eye_pos:
            pygame.draw.circle(surface, WHITE, pos, 4)
            pygame.draw.circle(surface, BLACK, pos, 2)
            
        pygame.draw.line(surface, BLACK, 
                        (self.position.x - camera_offset + 6, self.position.y + 4),
                        (self.position.x - camera_offset + 10, self.position.y + 2), 2)
        pygame.draw.line(surface, BLACK, 
                        (self.position.x - camera_offset + 24, self.position.y + 4),
                        (self.position.x - camera_offset + 20, self.position.y + 2), 2)

class Platform:
    def __init__(self, x, y, width, height, color=LIGHT_BROWN, is_spike=False, is_cloud=False):
        self.position = Point(x, y)
        self.size = Size(width, height)
        self.color = color
        self.is_spike = is_spike
        self.is_cloud = is_cloud
        
    def draw(self, surface, camera_offset):
        x_pos = self.position.x - camera_offset
        
        if self.is_cloud:
            base_rect = (x_pos, self.position.y, self.size.width, 15)
            pygame.draw.rect(surface, (250, 250, 250), base_rect)
            pygame.draw.rect(surface, (200, 200, 200), base_rect, 2)
            
            fluffs = [
                (x_pos + 10, self.position.y - 8, 25, 18),
                (x_pos + 40, self.position.y - 5, 35, 22),
                (x_pos + 90, self.position.y - 6, 30, 20),
                (x_pos + 140, self.position.y - 8, 25, 18)
            ]
            for fluff in fluffs:
                pygame.draw.ellipse(surface, (250, 250, 250), fluff)
                pygame.draw.ellipse(surface, (200, 200, 200), fluff, 1)
            return
        elif self.is_spike:
            pygame.draw.rect(surface, (140, 140, 140), 
                           (x_pos, self.position.y, self.size.width, self.size.height))
            pygame.draw.rect(surface, BLACK, 
                           (x_pos, self.position.y, self.size.width, self.size.height), 2)
            
            for i in range(0, self.size.width, 15):
                spike_points = [
                    (x_pos + i, self.position.y + self.size.height),
                    (x_pos + i + 7, self.position.y + self.size.height - 12),
                    (x_pos + i + 14, self.position.y + self.size.height)
                ]
                pygame.draw.polygon(surface, (100, 100, 100), spike_points)
                pygame.draw.polygon(surface, BLACK, spike_points, 1)
            return
            
        pygame.draw.rect(surface, self.color, 
                        (x_pos, self.position.y, self.size.width, self.size.height))
        pygame.draw.rect(surface, (80, 45, 30), 
                        (x_pos, self.position.y, self.size.width, self.size.height), 2)
        
        for i in range(0, self.size.width, 20):
            for j in range(0, self.size.height, 15):
                brick_x = x_pos + i
                brick_y = self.position.y + j
                pygame.draw.rect(surface, (self.color.r-20, self.color.g-20, self.color.b-20),
                               (brick_x, brick_y, 18, 13))
                
        pygame.draw.line(surface, (self.color.r+20, self.color.g+20, self.color.b+20),
                        (x_pos + self.size.width - 1, self.position.y),
                        (x_pos + self.size.width - 1, self.position.y + self.size.height), 2)
        pygame.draw.line(surface, (self.color.r+20, self.color.g+20, self.color.b+20),
                        (x_pos, self.position.y),
                        (x_pos + self.size.width, self.position.y), 2)

class Coin:
    def __init__(self, x, y):
        self.position = Point(x, y)
        self.collected = False
        self.animation_offset = 0
        self.rotation = 0
        self.flash = 0
        
    def update(self):
        if self.collected:
            return
        self.animation_offset = math.sin(pygame.time.get_ticks() * 0.03) * 3
        self.rotation = (pygame.time.get_ticks() % 360) * 2
        self.flash = math.sin(pygame.time.get_ticks() * 0.1)
        
    def draw(self, surface, camera_offset):
        if self.collected:
            return
            
        coin_y = self.position.y + self.animation_offset
        coin_x = self.position.x - camera_offset
        coin_size = 15
        
        pygame.draw.circle(surface, YELLOW, (coin_x, coin_y), coin_size)
        
        if self.flash > 0.5:
            pygame.draw.ellipse(surface, (255, 255, 200),
                              (coin_x - coin_size*0.7, coin_y - coin_size*0.5, 
                               coin_size*1.4, coin_size*1.0))
        
        pygame.draw.line(surface, ORANGE,
                       (coin_x - math.sin(math.radians(self.rotation)) * coin_size * 0.7,
                        coin_y - math.cos(math.radians(self.rotation)) * coin_size * 0.7),
                       (coin_x + math.sin(math.radians(self.rotation)) * coin_size * 0.7,
                        coin_y + math.cos(math.radians(self.rotation)) * coin_size * 0.7), 
                       3)
        
        pygame.draw.circle(surface, (200, 170, 0), (coin_x, coin_y), coin_size, 2)

class DialogBox:
    def __init__(self, text, x, y, width, height):
        self.text = text
        self.position = Point(x, y)
        self.size = Size(width, height)
        self.timer = 0
        self.typing_index = 0
        self.open = False
        
    def update(self):
        self.timer += 1
        if self.typing_index < len(self.text) and self.timer % 3 == 0:
            self.typing_index += 1
            
    def open_box(self):
        self.open = True
        self.timer = 0
        self.typing_index = 0
            
    def draw(self, surface):
        if not self.open:
            return
            
        pygame.draw.rect(surface, PAPER_YELLOW, 
                       (self.position.x, self.position.y, self.size.width, self.size.height))
        pygame.draw.rect(surface, BLACK, 
                       (self.position.x, self.position.y, self.size.width, self.size.height), 3)
        
        displayed_text = self.text[:self.typing_index]
        VectorFont.render_text(surface, displayed_text, 
                            self.position.x + 20, self.position.y + 20, 
                            22, BLACK)
        
        if self.typing_index == len(self.text) and self.timer % 20 < 10:
            arrow_y = self.position.y + self.size.height - 18
            pygame.draw.polygon(surface, BLACK, [
                (self.position.x + self.size.width - 25, arrow_y),
                (self.position.x + self.size.width - 15, arrow_y),
                (self.position.x + self.size.width - 20, arrow_y + 7)
            ])

class Camera:
    def __init__(self):
        self.offset = 0
        self.target_offset = 0
        
    def update(self, target_x):
        self.target_offset = target_x - WIDTH//2
        self.offset += (self.target_offset - self.offset) * CAMERA_SMOOTHNESS
        
    def apply(self, position):
        return position - self.offset

class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def add_particles(self, position, count, color, velocity_range_x=(-2.5, 2.5), velocity_range_y=(-3.5, -1.5), lifetime=30):
        for _ in range(count):
            self.particles.append([
                position.x, position.y,
                random.uniform(*velocity_range_x), 
                random.uniform(*velocity_range_y),
                lifetime,
                color
            ])
            
    def update(self):
        for p in self.particles[:]:
            p[0] += p[2]
            p[1] += p[3]
            p[3] += 0.15
            p[4] -= 1
                
            if p[4] <= 0:
                self.particles.remove(p)
    
    def draw(self, surface, camera_offset):
        for p in self.particles:
            pygame.draw.circle(surface, p[5], 
                           (int(p[0] - camera_offset), int(p[1])), 
                           max(1, int(p[4] / 10)))

def draw_background(surface, camera_offset):
    for i in range(HEIGHT//2):
        color_val = 140 + int(i/HEIGHT*80)
        pygame.draw.line(surface, (color_val, color_val, 255), 
                       (0, i), (WIDTH, i))
    
    mountains = [
        (0, HEIGHT//2, WIDTH//4, HEIGHT//3, 30),
        (WIDTH//5, HEIGHT//2-20, WIDTH//4, HEIGHT//2.5, 50),
        (WIDTH//1.8, HEIGHT//2, WIDTH//4, HEIGHT//3, 60)
    ]
    
    for x, y, w, h, offset in mountains:
        adjusted_x = (x - camera_offset * 0.1) % (WIDTH + w) - w
        pygame.draw.polygon(surface, (100, 120, 160), [
            (adjusted_x, y),
            (adjusted_x + w//2, y - h),
            (adjusted_x + w, y),
            (adjusted_x + w, HEIGHT),
            (adjusted_x, HEIGHT)
        ])
        pygame.draw.line(surface, BLACK, (adjusted_x, y), (adjusted_x + w//2, y - h), 2)
        pygame.draw.line(surface, BLACK, (adjusted_x + w//2, y - h), (adjusted_x + w, y), 2)
        
    cloud_offset = (camera_offset * 0.2) % WIDTH
    clouds = [
        (cloud_offset - 150, 50, 100, 40),
        (cloud_offset, 80, 120, 35),
        (cloud_offset + 200, 40, 90, 30)
    ]
    
    for x, y, w, h in clouds:
        pygame.draw.ellipse(surface, (250, 250, 255), (x, y, w, h))
        pygame.draw.ellipse(surface, (200, 200, 255), (x, y, w, h), 2)

def draw_ground(surface, camera_offset):
    pygame.draw.rect(surface, GROUND_COLOR, 
                   (0 - camera_offset, GROUND_LEVEL, WIDTH*2, HEIGHT - GROUND_LEVEL))
    
    pygame.draw.rect(surface, GREEN, 
                   (0 - camera_offset, GROUND_LEVEL, WIDTH*2, 12))
    
    for i in range(0, WIDTH*2, 20):
        height = random.randint(0, 5)
        for j in range(4):
            line_x = i - camera_offset + j * 4
            pygame.draw.line(surface, GREEN, 
                           (line_x, GROUND_LEVEL),
                           (line_x, GROUND_LEVEL - height - j//2), 1)
    
    for i in range(0, WIDTH*2, 15):
        x = i - camera_offset
        pygame.draw.line(surface, (100, 60, 40), 
                       (x, GROUND_LEVEL + 10), (x, GROUND_LEVEL + 40), 1)

def draw_ui(surface, coins, lives):
    panel_y = 20
    pygame.draw.rect(surface, (70, 40, 30, 220), 
                   (WIDTH//2 - 100, panel_y, 200, 50), 
                   border_radius=15)
    pygame.draw.rect(surface, BLACK, 
                   (WIDTH//2 - 100, panel_y, 200, 50), 
                   3, border_radius=15)
    
    pygame.draw.circle(surface, YELLOW, (WIDTH//2 - 50, panel_y + 25), 15)
    pygame.draw.circle(surface, ORANGE, (WIDTH//2 - 50, panel_y + 25), 15, 2)
    
    pygame.draw.circle(surface, (220, 220, 100), (WIDTH//2 + 50, panel_y + 25), 13)
    pygame.draw.circle(surface, (180, 180, 70), (WIDTH//2 + 50, panel_y + 25), 13, 2)
    
    VectorFont.render_text(surface, f"x{coins}", 
                        WIDTH//2 - 25, panel_y + 10, 
                        24, WHITE)
    
    VectorFont.render_text(surface, f"x{lives}", 
                        WIDTH//2 + 75, panel_y + 10, 
                        24, WHITE)
    
    VectorFont.render_text(surface, "KOOP THE KOOPA", 
                        WIDTH//2 - 90, HEIGHT - 40, 
                        26, YELLOW)
    
    if pygame.time.get_ticks() < 10000:
        VectorFont.render_text(surface, "Hold SHIFT to run", 
                            WIDTH//2 - 80, HEIGHT - 90, 
                            18, WHITE)

def draw_main_menu(surface, selection):
    surface.fill(MENU_BG)
    
    for i in range(0, WIDTH, 40):
        for j in range(0, HEIGHT, 40):
            pygame.draw.rect(surface, (70, 130, 210), (i, j, 35, 35), 1)
    
    pygame.draw.rect(surface, RED, (0, 50, WIDTH, 120))
    pygame.draw.rect(surface, (180, 40, 40), (0, 50, WIDTH, 120), 3)
    
    VectorFont.render_text(surface, "PAPER MARIO", 
                        WIDTH//2 - 180, 70, 
                        60, YELLOW, BLACK, 4)
    
    VectorFont.render_text(surface, "KOOPA ENGINE 1.0", 
                        WIDTH//2 - 220, 130, 
                        48, WHITE, BLACK, 3)
    
    koopa_x = WIDTH//2
    koopa_y = HEIGHT//2 + 40
    
    pygame.draw.ellipse(surface, KOOPA_SHELL, 
                      (koopa_x - 60, koopa_y - 40, 120, 60))
    pygame.draw.ellipse(surface, BLACK, 
                      (koopa_x - 60, koopa_y - 40, 120, 60), 3)
    
    pygame.draw.ellipse(surface, KOOPA_GREEN, 
                      (koopa_x - 40, koopa_y - 70, 80, 40))
    pygame.draw.ellipse(surface, BLACK, 
                      (koopa_x - 40, koopa_y - 70, 80, 40), 2)
    
    pygame.draw.circle(surface, WHITE, (koopa_x - 15, koopa_y - 55), 10)
    pygame.draw.circle(surface, WHITE, (koopa_x + 15, koopa_y - 55), 10)
    pygame.draw.circle(surface, BLACK, (koopa_x - 15, koopa_y - 55), 4)
    pygame.draw.circle(surface, BLACK, (koopa_x + 15, koopa_y - 55), 4)
    
    bandana_points = [
        (koopa_x - 50, koopa_y - 70),
        (koopa_x - 30, koopa_y - 100),
        (koopa_x + 30, koopa_y - 100),
        (koopa_x + 50, koopa_y - 70)
    ]
    pygame.draw.polygon(surface, BANDANA_BLUE, bandana_points)
    pygame.draw.polygon(surface, BLACK, bandana_points, 2)
    
    options = [
        "START GAME",
        "CONTROLS",
        "QUIT"
    ]
    
    for i, option in enumerate(options):
        y_pos = HEIGHT//2 + 120 + i * 50
        color = WHITE if i != selection else YELLOW
        
        if i == selection:
            pygame.draw.rect(surface, MENU_HIGHLIGHT, 
                          (WIDTH//2 - 110, y_pos - 25, 220, 40), 
                          border_radius=10)
            pygame.draw.rect(surface, BLACK, 
                          (WIDTH//2 - 110, y_pos - 25, 220, 40), 
                          3, border_radius=10)
        
        VectorFont.render_text(surface, option, 
                            WIDTH//2 - 80, y_pos - 10, 
                            30, color)
    
    VectorFont.render_text(surface, "© 2023 KOOPA STUDIOS", 
                        WIDTH//2 - 120, HEIGHT - 30, 
                        20, WHITE)

def draw_boot_screen(surface, progress):
    surface.fill((30, 30, 60))
    
    bar_width = 400
    bar_height = 30
    bar_x = (WIDTH - bar_width) // 2
    bar_y = HEIGHT // 2 + 50
    
    pygame.draw.rect(surface, (60, 60, 100), 
                   (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(surface, BLACK, 
                   (bar_x, bar_y, bar_width, bar_height), 3)
    
    fill_width = int(bar_width * progress)
    pygame.draw.rect(surface, BLUE, 
                   (bar_x, bar_y, fill_width, bar_height))
    
    VectorFont.render_text(surface, "LOADING KOOPA ENGINE...", 
                        WIDTH//2 - 180, HEIGHT//2 - 30, 
                        36, WHITE)
    
    percent = int(progress * 100)
    VectorFont.render_text(surface, f"{percent}%", 
                        WIDTH//2 - 30, bar_y + bar_height + 20, 
                        24, WHITE)
    
    for i in range(20):
        size = random.randint(5, 15)
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT//2 - 50)
        pygame.draw.circle(surface, (100, 100, 200), (x, y), size)
        pygame.draw.circle(surface, (70, 70, 180), (x, y), size, 1)

def create_stage():
    platforms = [
        Platform(300, GROUND_LEVEL - 120, 140, 20, (180, 160, 130), is_cloud=True),
        Platform(600, GROUND_LEVEL - 180, 110, 20, (150, 200, 150)),
        Platform(900, GROUND_LEVEL - 80, 120, 20, LIGHT_BROWN),
        Platform(1200, GROUND_LEVEL - 160, 70, 20, (200, 150, 100)),
        Platform(1500, GROUND_LEVEL - 220, 80, 20, LIGHT_BROWN),
        Platform(1800, GROUND_LEVEL - 140, 100, 20, (200, 150, 100)),
        Platform(400, GROUND_LEVEL - 40, 80, 20, is_spike=True),
        Platform(1100, GROUND_LEVEL - 40, 80, 20, is_spike=True),
    ]
    
    coins = [
        Coin(320, GROUND_LEVEL - 150),
        Coin(650, GROUND_LEVEL - 220),
        Coin(950, GROUND_LEVEL - 120),
        Coin(1230, GROUND_LEVEL - 190),
        Coin(1530, GROUND_LEVEL - 250),
        Coin(1840, GROUND_LEVEL - 170),
    ]
    
    goombas = [
        Goomba(100, GROUND_LEVEL),
        Goomba(800, GROUND_LEVEL),
        Goomba(1400, GROUND_LEVEL),
        Goomba(1900, GROUND_LEVEL, 150)
    ]
    
    return platforms, coins, goombas

def main():
    game_state = GameState.MENU
    menu_selection = 0
    boot_progress = 0
    
    platforms, coins, goombas = create_stage()
    koops = Koops(400, GROUND_LEVEL - 100)
    
    camera = Camera()
    dialog = DialogBox("JUMP ON ENEMIES TO DEFEAT THEM! WATCH OUT FOR SPIKES!", 
                      WIDTH//2 - 250, 100, 500, 80)
    
    particle_system = ParticleSystem()
    
    collected_coins = 0
    lives = 3
    clock = pygame.time.Clock()
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if game_state == GameState.MENU:
                    if event.key == pygame.K_DOWN:
                        menu_selection = (menu_selection + 1) % 3
                    elif event.key == pygame.K_UP:
                        menu_selection = (menu_selection - 1) % 3
                    elif event.key == pygame.K_RETURN:
                        if menu_selection == 0:
                            game_state = GameState.BOOT
                            boot_progress = 0
                        elif menu_selection == 2:
                            running = False
                
                elif game_state == GameState.GAMEPLAY:
                    if event.key in (pygame.K_SPACE, pygame.K_w):
                        koops.jump()
                    elif event.key == pygame.K_s:
                        koops.crouch(True)
                    elif event.key == pygame.K_LSHIFT:
                        koops.run(True)
                
                elif game_state == GameState.GAME_OVER and event.key == pygame.K_r:
                    platforms, coins, goombas = create_stage()
                    koops = Koops(400, GROUND_LEVEL - 100)
                    collected_coins = 0
                    lives = 3
                    game_state = GameState.GAMEPLAY
            
            elif event.type == pygame.KEYUP and game_state == GameState.GAMEPLAY:
                if event.key == pygame.K_s:
                    koops.crouch(False)
                elif event.key == pygame.K_LSHIFT:
                    koops.run(False)
        
        if game_state == GameState.MENU:
            draw_main_menu(screen, menu_selection)
        
        elif game_state == GameState.BOOT:
            boot_progress += 0.02
            if boot_progress >= 1.0:
                game_state = GameState.GAMEPLAY
                dialog.open_box()
            draw_boot_screen(screen, boot_progress)
        
        elif game_state in (GameState.GAMEPLAY, GameState.GAME_OVER):
            camera.update(koops.position.x)
            
            screen.fill(BACKGROUND)
            draw_background(screen, camera.offset)
            
            keys = pygame.key.get_pressed()
            dx = keys[pygame.K_d] - keys[pygame.K_a]
            koops.move(dx, platforms)
            
            koops.update(platforms)
            dialog.update()
            particle_system.update()
            
            for coin in coins:
                coin.update()
                if not coin.collected:
                    dist = math.sqrt((koops.position.x - coin.position.x)**2 + 
                                    (koops.position.y - coin.position.y)**2)
                    if dist < 30:
                        coin.collected = True
                        collected_coins += 1
                        particle_system.add_particles(coin.position, 10, YELLOW)
            
            for goomba in goombas:
                goomba.update()
                if not goomba.crushed:
                    if (koops.position.x + koops.size.width > goomba.position.x + 5 and 
                        koops.position.x < goomba.position.x + goomba.size.width - 5 and
                        koops.position.y + koops.size.height - 5 > goomba.position.y and
                        koops.position.y < goomba.position.y + goomba.size.height):
                        
                        if koops.position.y + koops.size.height < goomba.position.y + 10 and koops.velocity_y > 0:
                            goomba.crushed = True
                            koops.velocity_y = -JUMP_POWER * 0.7
                            particle_system.add_particles(goomba.position, 15, BROWN)
                        elif koops.invincible == 0:
                            koops.damage()
            
            for platform in platforms:
                if platform.is_spike:
                    if (koops.position.x + koops.size.width > platform.position.x and 
                        koops.position.x < platform.position.x + platform.size.width and
                        koops.position.y + koops.size.height > platform.position.y and
                        koops.position.y < platform.position.y + platform.size.height):
                        koops.damage()
                        koops.velocity_y = -8
                        if koops.position.x < platform.position.x + platform.size.width//2:
                            koops.position = Point(platform.position.x - koops.size.width - 5, koops.position.y)
                        else:
                            koops.position = Point(platform.position.x + platform.size.width + 5, koops.position.y)
                        particle_system.add_particles(koops.position, 15, RED, (-3, 3), (-5, -3), 25)
            
            draw_ground(screen, camera.offset)
            
            for platform in platforms:
                platform.draw(screen, camera.offset)
            
            for coin in coins:
                coin.draw(screen, camera.offset)
            
            for goomba in goombas:
                goomba.draw(screen, camera.offset)
            
            koops.draw(screen)
            particle_system.draw(screen, camera.offset)
            draw_ui(screen, collected_coins, lives)
            dialog.draw(screen)
            
            if koops.hit_points <= 0:
                lives -= 1
                koops.hit_points = 3
                koops.position = Point(camera.offset + WIDTH//2, GROUND_LEVEL - 100)
                koops.velocity_y = 0
            
            if lives <= 0:
                game_state = GameState.GAME_OVER
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))
                screen.blit(overlay, (0, 0))
                
                VectorFont.render_text(screen, "GAME OVER", 
                                    WIDTH//2 - 100, HEIGHT//2 - 50, 
                                    50, RED, WHITE, 5)
                VectorFont.render_text(screen, "PRESS R TO RESTART", 
                                    WIDTH//2 - 140, HEIGHT//2 + 30, 
                                    28, YELLOW)
        
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
