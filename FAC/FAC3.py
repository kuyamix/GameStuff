import pygame
import random
import math
import sys
import traceback

# Initialize
pygame.init()

# ============ SCREEN SETUP ============
# Get display info for better PC experience
info = pygame.display.Info()
SCREEN_WIDTH = min(940, int(info.current_w * 0.7))
SCREEN_HEIGHT = min(2030, int(info.current_h * 0.85))
# Ensure minimum size
SCREEN_WIDTH = max(SCREEN_WIDTH, 800)
SCREEN_HEIGHT = max(SCREEN_HEIGHT, 600)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("🎯 FAC - MRLS Support! (PC Edition)")
clock = pygame.time.Clock()

# ============ MASSIVE MAP ============
MAP_WIDTH = 4500
MAP_HEIGHT = 4500

# Camera system
camera_x = 0
camera_y = 0
zoom_level = 1.0
min_zoom = 0.25
max_zoom = 2.0
zoom_speed = 0.05

# ============ COLORS ============
BLACK = (10, 10, 20)
WHITE = (255, 255, 255)
RED = (200, 30, 30)
GREEN = (50, 200, 50)
BLUE = (30, 150, 255)
PURPLE = (180, 50, 255)
YELLOW = (255, 255, 50)
ORANGE = (255, 150, 30)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
FIRE_ORANGE = (255, 100, 0)
LIGHT_BLUE = (100, 200, 255)
DARK_GREEN = (20, 80, 20)
BROWN = (139, 69, 19)
DARK_RED = (139, 0, 0)
GOLD = (255, 215, 0)
DARK_PURPLE = (75, 0, 130)
CYAN = (0, 255, 255)
LIME = (50, 255, 50)
DARK_BLUE = (0, 0, 139)
CRIMSON = (220, 20, 60)
MAROON = (128, 0, 0)
STEEL = (70, 130, 180)
FOREST = (34, 139, 34)
DARK_ORANGE = (255, 140, 0)
SLATE = (112, 128, 144)

# ============ PLAYER ============
player_size = 22
player_x = MAP_WIDTH // 2
player_y = MAP_HEIGHT // 2
player_health = 100
player_max_health = 100
player_speed = 4.0
level = 1
xp = 0
xp_to_next = 30
game_time = 0
level_up_notifications = []

# ============ LEVEL SYSTEM ============
UNLOCK_LEVELS = {
    'strafe': 1,
    'mortar': 3,
    'mrls': 6
}

BASE_STATS = {
    'health_bonus': 5,
    'speed_bonus': 0.1,
    'cooldown_reduction': 0.02
}

# ============ ABILITIES ============
aiming_mode = False
aiming_ability = None
aim_x = 0
aim_y = 0
aim_angle = 0

# Strafing Run
strafe_cooldown = 0
strafe_max_cooldown = 300
strafe_damage = 35
strafe_range = 300
strafe_duration = 0
strafe_active = False
strafe_x = 0
strafe_y = 0
strafe_angle = 0
strafe_particles = []
strafe_bullets = []
strafe_pass = 0
strafe_max_passes = 3

# Mortar Strike
mortar_cooldown = 0
mortar_max_cooldown = 400
mortar_damage = 60
mortar_radius = 160
mortar_impact_timer = 0
mortar_target_x = 0
mortar_target_y = 0
mortar_phase = 0
mortar_flash = 0
mortar_shells = []
mortar_impact_effects = []

# MRLS Strike
mrls_cooldown = 0
mrls_max_cooldown = 700
mrls_active = False
mrls_rockets = []
mrls_explosions = []
mrls_target_x = 0
mrls_target_y = 0
mrls_fire_timer = 0
mrls_rockets_fired = 0
mrls_total_rockets = 5
mrls_phase = 0
mrls_flash = 0
mrls_warning_timer = 0

# ============ ENEMIES ============
enemies = []
enemy_spawn_timer = 0
enemy_spawn_delay = 35
max_enemies = 60
enemies_killed = 0
gems = []

ENEMY_TYPES = {
    'grunt': {'hp': 25, 'speed': 1.5, 'size': 18, 'color': RED, 'xp': 10, 'damage': 8},
    'tank': {'hp': 100, 'speed': 0.7, 'size': 30, 'color': PURPLE, 'xp': 30, 'damage': 18},
    'fast': {'hp': 15, 'speed': 3.2, 'size': 14, 'color': (255, 100, 100), 'xp': 12, 'damage': 6},
    'heavy': {'hp': 150, 'speed': 0.5, 'size': 38, 'color': DARK_RED, 'xp': 40, 'damage': 25},
    'elite': {'hp': 75, 'speed': 1.3, 'size': 24, 'color': GOLD, 'xp': 25, 'damage': 15},
    'juggernaut': {'hp': 300, 'speed': 0.35, 'size': 48, 'color': CRIMSON, 'xp': 60, 'damage': 35},
    'behemoth': {'hp': 500, 'speed': 0.25, 'size': 58, 'color': MAROON, 'xp': 80, 'damage': 45},
    'colossus': {'hp': 800, 'speed': 0.18, 'size': 70, 'color': DARK_PURPLE, 'xp': 100, 'damage': 55},
    'titan': {'hp': 1200, 'speed': 0.12, 'size': 85, 'color': SLATE, 'xp': 130, 'damage': 65},
    'leviathan': {'hp': 2000, 'speed': 0.08, 'size': 100, 'color': STEEL, 'xp': 160, 'damage': 80}
}

# ============ PC CONTROLS ============
# Keyboard movement state
keys_pressed = {'up': False, 'down': False, 'left': False, 'right': False}
mouse_held = False

# ============ UI ELEMENTS - SCALED FOR SCREEN ============
ui_scale = min(SCREEN_WIDTH / 940, SCREEN_HEIGHT / 2030)

button_size = int(80 * ui_scale)
button_spacing = int(10 * ui_scale)
button_margin = int(20 * ui_scale)

button_x = SCREEN_WIDTH - button_size - button_margin
button_y_start = SCREEN_HEIGHT - button_size * 3 - button_spacing * 2 - button_margin

strafe_button = pygame.Rect(button_x, button_y_start, button_size, button_size)
mortar_button = pygame.Rect(button_x, button_y_start + button_size + button_spacing, button_size, button_size)
mrls_button = pygame.Rect(button_x, button_y_start + button_size * 2 + button_spacing * 2, button_size, button_size)

upgrade_button = pygame.Rect(SCREEN_WIDTH//2 - int(80 * ui_scale), SCREEN_HEIGHT - int(80 * ui_scale), int(160 * ui_scale), int(50 * ui_scale))
cancel_button = pygame.Rect(SCREEN_WIDTH//2 - int(50 * ui_scale), SCREEN_HEIGHT - int(50 * ui_scale), int(100 * ui_scale), int(40 * ui_scale))

zoom_button_size = int(45 * ui_scale)
zoom_in_button = pygame.Rect(SCREEN_WIDTH - zoom_button_size - int(10 * ui_scale), int(120 * ui_scale), zoom_button_size, zoom_button_size)
zoom_out_button = pygame.Rect(SCREEN_WIDTH - zoom_button_size - int(10 * ui_scale), int(170 * ui_scale), zoom_button_size, zoom_button_size)

minimap_size = int(120 * ui_scale)
minimap_rect = pygame.Rect(int(15 * ui_scale), SCREEN_HEIGHT - minimap_size - int(15 * ui_scale), minimap_size, minimap_size)

font_scale = ui_scale
font_size = max(int(20 * font_scale), 14)
small_font = pygame.font.Font(None, font_size)
medium_font = pygame.font.Font(None, int(font_size * 1.3))
big_font = pygame.font.Font(None, int(font_size * 2))
huge_font = pygame.font.Font(None, int(font_size * 3))

# ============ HELPER FUNCTIONS ============
def world_to_screen(world_x, world_y):
    return (world_x - camera_x) * zoom_level + SCREEN_WIDTH // 2, (world_y - camera_y) * zoom_level + SCREEN_HEIGHT // 2

def screen_to_world(screen_x, screen_y):
    return (screen_x - SCREEN_WIDTH // 2) / zoom_level + camera_x, (screen_y - SCREEN_HEIGHT // 2) / zoom_level + camera_y

def distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)

def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))

def is_ability_unlocked(ability):
    return level >= UNLOCK_LEVELS.get(ability, 999)

def spawn_enemy():
    global enemies, game_time
    
    available_types = ['grunt']
    
    time_seconds = game_time // 60
    
    if time_seconds > 10: available_types.append('fast')
    if time_seconds > 20: available_types.append('tank')
    if time_seconds > 35: available_types.append('heavy')
    if time_seconds > 50: available_types.append('elite')
    if time_seconds > 70: available_types.append('juggernaut')
    if time_seconds > 90: available_types.append('behemoth')
    if time_seconds > 120: available_types.append('colossus')
    if time_seconds > 160: available_types.append('titan')
    if time_seconds > 200: available_types.append('leviathan')
    
    enemy_type = 'grunt'
    roll = random.random()
    
    if time_seconds > 200 and roll < 0.05:
        enemy_type = 'leviathan'
    elif time_seconds > 160 and roll < 0.08:
        enemy_type = 'titan'
    elif time_seconds > 120 and roll < 0.12:
        enemy_type = 'colossus'
    elif time_seconds > 90 and roll < 0.18:
        enemy_type = 'behemoth'
    elif time_seconds > 70 and roll < 0.25:
        enemy_type = 'juggernaut'
    elif time_seconds > 50 and roll < 0.35:
        enemy_type = 'elite'
    elif time_seconds > 35 and roll < 0.50:
        enemy_type = 'heavy'
    elif time_seconds > 20 and roll < 0.65:
        enemy_type = 'tank'
    elif time_seconds > 10 and roll < 0.80:
        enemy_type = 'fast'
    else:
        enemy_type = 'grunt'
    
    side = random.randint(0, 3)
    if side == 0:
        x, y = random.randint(0, MAP_WIDTH), -30
    elif side == 1:
        x, y = random.randint(0, MAP_WIDTH), MAP_HEIGHT + 30
    elif side == 2:
        x, y = -30, random.randint(0, MAP_HEIGHT)
    else:
        x, y = MAP_WIDTH + 30, random.randint(0, MAP_HEIGHT)
    
    stats = ENEMY_TYPES[enemy_type].copy()
    
    time_scale = 1 + (time_seconds / 60) * 0.15
    stats['hp'] = int(stats['hp'] * time_scale)
    stats['speed'] = stats['speed'] * (1 + (time_seconds / 60) * 0.03)
    stats['xp'] = int(stats['xp'] * time_scale)
    stats['damage'] = int(stats['damage'] * time_scale)
    
    enemies.append(Enemy(x, y, stats['speed'], stats['hp'], stats['size'], 
                       stats['color'], stats['xp'], enemy_type, stats['damage']))

class Enemy:
    def __init__(self, x, y, speed, hp, size, color, xp_value, enemy_type, damage):
        self.x = x
        self.y = y
        self.speed = speed
        self.hp = hp
        self.max_hp = hp
        self.size = size
        self.color = color
        self.xp_value = xp_value
        self.type = enemy_type
        self.damage = damage
        self.rect = pygame.Rect(x - size//2, y - size//2, size, size)
        self.hit_timer = 0
        self.knockback_x = 0
        self.knockback_y = 0
        self.attack_cooldown = 0
        self.angle = random.uniform(0, 2 * math.pi)
    
    def move_towards_player(self, px, py):
        dx = px - self.x
        dy = py - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            if self.knockback_x != 0 or self.knockback_y != 0:
                self.x += self.knockback_x * 0.5
                self.y += self.knockback_y * 0.5
                self.knockback_x *= 0.9
                self.knockback_y *= 0.9
                if abs(self.knockback_x) < 0.1: self.knockback_x = 0
                if abs(self.knockback_y) < 0.1: self.knockback_y = 0
            else:
                move_speed = self.speed * (0.8 if self.type in ['heavy', 'juggernaut', 'behemoth', 'colossus', 'titan', 'leviathan'] else 1.0)
                self.x += (dx / dist) * move_speed
                self.y += (dy / dist) * move_speed
        
        self.rect.x = self.x - self.size//2
        self.rect.y = self.y - self.size//2
        
        if self.hit_timer > 0: self.hit_timer -= 1
        if self.attack_cooldown > 0: self.attack_cooldown -= 1
        if dist > 0: self.angle = math.atan2(dy, dx)
    
    def draw(self, screen, offset_x, offset_y, zoom):
        screen_x = (self.x - offset_x) * zoom + SCREEN_WIDTH // 2
        screen_y = (self.y - offset_y) * zoom + SCREEN_HEIGHT // 2
        size = self.size * zoom
        
        if screen_x < -size or screen_x > SCREEN_WIDTH + size or screen_y < -size or screen_y > SCREEN_HEIGHT + size:
            return
        
        if self.hp < self.max_hp:
            bar_width = size
            bar_height = 4 * zoom
            health_ratio = max(0, self.hp / self.max_hp)
            pygame.draw.rect(screen, RED, (screen_x - bar_width//2, screen_y - size//2 - 10 * zoom, bar_width, bar_height))
            pygame.draw.rect(screen, GREEN, (screen_x - bar_width//2, screen_y - size//2 - 10 * zoom, bar_width * health_ratio, bar_height))
        
        color = WHITE if self.hit_timer > 0 else self.color
        
        if self.type in ["tank", "heavy", "juggernaut", "behemoth", "colossus", "titan", "leviathan"]:
            if self.type == "juggernaut":
                points = []
                for i in range(6):
                    angle = self.angle + i * math.pi / 3
                    r = size // 2
                    points.append((screen_x + math.cos(angle) * r, screen_y + math.sin(angle) * r))
                pygame.draw.polygon(screen, color, points)
                pygame.draw.polygon(screen, (color[0]//2, color[1]//2, color[2]//2), points, 2)
            elif self.type == "behemoth":
                pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), int(size//2))
                for i in range(8):
                    angle = self.angle + i * math.pi / 4
                    pygame.draw.arc(screen, (color[0]//2, color[1]//2, color[2]//2), 
                                   (screen_x - size//2, screen_y - size//2, size, size), 
                                   angle, angle + math.pi/8, 3)
            elif self.type == "colossus":
                points = [(screen_x, screen_y - size//2),
                         (screen_x + size//2, screen_y),
                         (screen_x, screen_y + size//2),
                         (screen_x - size//2, screen_y)]
                pygame.draw.polygon(screen, color, points)
                pygame.draw.polygon(screen, (color[0]//2, color[1]//2, color[2]//2), points, 3)
            elif self.type == "titan":
                points = []
                for i in range(8):
                    angle = self.angle + i * math.pi / 4
                    r = size // 2
                    points.append((screen_x + math.cos(angle) * r, screen_y + math.sin(angle) * r))
                pygame.draw.polygon(screen, color, points)
                pygame.draw.polygon(screen, (color[0]//2, color[1]//2, color[2]//2), points, 2)
            elif self.type == "leviathan":
                for i in range(3):
                    r = size//2 - i * (size//6)
                    pygame.draw.circle(screen, (color[0] - i*30, color[1] - i*30, color[2] - i*30), 
                                     (int(screen_x), int(screen_y)), int(r), 2)
                pygame.draw.circle(screen, (255, 200, 200), (int(screen_x), int(screen_y)), int(size//4))
            else:
                pygame.draw.rect(screen, color, (screen_x - size//2, screen_y - size//2, size, size))
                pygame.draw.rect(screen, (color[0]//2, color[1]//2, color[2]//2), 
                               (screen_x - size//2 + 4, screen_y - size//2 + 4, size - 8, size - 8))
        elif self.type == "fast":
            points = [(screen_x + math.cos(self.angle) * size//2, screen_y + math.sin(self.angle) * size//2),
                     (screen_x + math.cos(self.angle + 2.5) * size//2, screen_y + math.sin(self.angle + 2.5) * size//2),
                     (screen_x + math.cos(self.angle - 2.5) * size//2, screen_y + math.sin(self.angle - 2.5) * size//2)]
            pygame.draw.polygon(screen, color, points)
        elif self.type == "elite":
            pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), int(size//2))
            for i in range(8):
                angle = self.angle + i * math.pi / 4
                pygame.draw.circle(screen, GOLD, (int(screen_x + math.cos(angle) * size//2), 
                                                int(screen_y + math.sin(angle) * size//2)), int(size//6))
        else:
            pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), int(size//2))

class Gem:
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value
        self.rect = pygame.Rect(x - 8, y - 8, 16, 16)
        self.bob_timer = random.randint(0, 100)
        self.pull_speed = 0
    
    def update(self, px, py):
        self.bob_timer += 0.1
        dx = px - self.x
        dy = py - self.y
        dist = math.hypot(dx, dy)
        
        if dist < 200:
            self.pull_speed = min(self.pull_speed + 0.1, 5)
            if dist > 0:
                self.x += (dx / dist) * self.pull_speed
                self.y += (dy / dist) * self.pull_speed
        else:
            self.pull_speed = max(self.pull_speed - 0.05, 0)
        
        self.rect.x = self.x - 8
        self.rect.y = self.y - 8 + math.sin(self.bob_timer) * 2
    
    def draw(self, screen, offset_x, offset_y, zoom):
        screen_x = (self.x - offset_x) * zoom + SCREEN_WIDTH // 2
        screen_y = (self.y - offset_y) * zoom + SCREEN_HEIGHT // 2
        size = (8 + math.sin(self.bob_timer) * 1.5) * zoom
        
        if screen_x < -size or screen_x > SCREEN_WIDTH + size or screen_y < -size or screen_y > SCREEN_HEIGHT + size:
            return
        
        pygame.draw.circle(screen, YELLOW, (int(screen_x), int(screen_y)), int(size))
        pygame.draw.circle(screen, ORANGE, (int(screen_x) - 2, int(screen_y) - 2), int(size * 0.5))

# ============ ABILITY FUNCTIONS ============

def start_aiming(ability_type):
    global aiming_mode, aiming_ability, aim_x, aim_y
    
    if not is_ability_unlocked(ability_type):
        return False
    
    if ability_type == "strafe" and strafe_cooldown == 0:
        aiming_mode = True
        aiming_ability = "strafe"
        aim_x, aim_y = player_x, player_y
        return True
    elif ability_type == "mortar" and mortar_cooldown == 0 and is_ability_unlocked('mortar'):
        aiming_mode = True
        aiming_ability = "mortar"
        aim_x, aim_y = player_x, player_y
        return True
    elif ability_type == "mrls" and mrls_cooldown == 0 and is_ability_unlocked('mrls'):
        aiming_mode = True
        aiming_ability = "mrls"
        aim_x, aim_y = player_x, player_y
        return True
    return False

def confirm_aim():
    global aiming_mode, aiming_ability
    if aiming_mode:
        try:
            if aiming_ability == "strafe": 
                call_strafing_run(aim_x, aim_y)
            elif aiming_ability == "mortar": 
                call_mortar_strike(aim_x, aim_y)
            elif aiming_ability == "mrls": 
                call_mrls_strike(aim_x, aim_y)
        except:
            pass
        aiming_mode = False
        aiming_ability = None

def cancel_aim():
    global aiming_mode, aiming_ability
    aiming_mode = False
    aiming_ability = None

# ============ STRAFING RUN ============
def call_strafing_run(target_x, target_y):
    global strafe_active, strafe_x, strafe_y, strafe_angle, strafe_duration, strafe_cooldown
    global strafe_particles, strafe_bullets, strafe_pass
    
    if strafe_cooldown > 0: return False
    
    strafe_active = True
    strafe_x, strafe_y = target_x, target_y
    strafe_duration = 60
    strafe_cooldown = int(strafe_max_cooldown * (1.0 - (level - 1) * BASE_STATS['cooldown_reduction']))
    strafe_cooldown = max(strafe_cooldown, 60)
    strafe_pass = 0
    strafe_particles = []
    strafe_bullets = []
    
    edges = [(target_x, 0, -math.pi/2), (target_x, MAP_HEIGHT, math.pi/2), 
             (0, target_y, math.pi), (MAP_WIDTH, target_y, 0)]
    strafe_angle = min(edges, key=lambda e: abs(e[0] - target_x) + abs(e[1] - target_y))[2]
    return True

def execute_strafing_run():
    global strafe_particles, strafe_bullets, strafe_pass, strafe_active, strafe_duration
    global enemies, gems, enemies_killed
    
    if not strafe_active:
        return
    
    strafe_pass += 1
    
    for i in range(20):
        progress = i / 20
        offset = (progress - 0.5) * strafe_range
        x = strafe_x + math.cos(strafe_angle + math.pi/2) * offset
        y = strafe_y + math.sin(strafe_angle + math.pi/2) * offset
        
        x += random.uniform(-10, 10)
        y += random.uniform(-10, 10)
        
        for enemy in enemies[:]:
            if distance(enemy.x, enemy.y, x, y) < 50:
                enemy.hp -= strafe_damage + level * 2
                enemy.knockback_x = math.cos(strafe_angle) * 30
                enemy.knockback_y = math.sin(strafe_angle) * 30
                enemy.hit_timer = 15
                if enemy.hp <= 0:
                    gems.append(Gem(enemy.x, enemy.y, enemy.xp_value))
                    enemies.remove(enemy)
                    enemies_killed += 1
        
        strafe_bullets.append({
            'x': x,
            'y': y,
            'life': 20,
            'vx': math.cos(strafe_angle) * random.uniform(5, 10),
            'vy': math.sin(strafe_angle) * random.uniform(5, 10)
        })
        
        strafe_particles.append({
            'x': x,
            'y': y,
            'life': 30,
            'color': (255, random.randint(150, 255), 0),
            'size': random.randint(3, 10)
        })
    
    for bullet in strafe_bullets[:]:
        bullet['x'] += bullet['vx']
        bullet['y'] += bullet['vy']
        bullet['life'] -= 1
        if bullet['life'] <= 0:
            strafe_bullets.remove(bullet)
    
    for particle in strafe_particles[:]:
        particle['life'] -= 1
        particle['x'] += random.uniform(-3, 3)
        particle['y'] += random.uniform(-3, 3)
        if particle['life'] <= 0:
            strafe_particles.remove(particle)
    
    strafe_duration -= 1
    if strafe_duration <= 0:
        strafe_active = False
        strafe_particles.clear()
        strafe_bullets.clear()

# ============ MORTAR STRIKE ============
def call_mortar_strike(target_x, target_y):
    global mortar_phase, mortar_target_x, mortar_target_y, mortar_impact_timer, mortar_cooldown, mortar_shells
    
    if mortar_cooldown > 0 or not is_ability_unlocked('mortar'): return False
    
    mortar_target_x, mortar_target_y = target_x, target_y
    mortar_phase = 1
    mortar_impact_timer = 55
    mortar_cooldown = int(mortar_max_cooldown * (1.0 - (level - 1) * BASE_STATS['cooldown_reduction']))
    mortar_cooldown = max(mortar_cooldown, 80)
    
    mortar_shells = []
    for i in range(6):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(20, 100)
        mortar_shells.append({
            'x': target_x + math.cos(angle) * dist * 0.2,
            'y': -60 - i * 25,
            'target_x': target_x + math.cos(angle) * dist * 0.6,
            'target_y': target_y + math.sin(angle) * dist * 0.6,
            'speed': 5 + i * 0.5
        })
    return True

def execute_mortar_strike():
    global mortar_flash, mortar_phase, mortar_impact_effects
    global enemies, gems, enemies_killed
    
    for enemy in enemies[:]:
        dist = distance(enemy.x, enemy.y, mortar_target_x, mortar_target_y)
        if dist < mortar_radius:
            damage_mult = 1 - (dist / mortar_radius) * 0.3
            enemy.hp -= (mortar_damage + level * 4) * damage_mult
            if dist > 0:
                enemy.knockback_x = (enemy.x - mortar_target_x) / dist * 30
                enemy.knockback_y = (enemy.y - mortar_target_y) / dist * 30
            enemy.hit_timer = 20
            if enemy.hp <= 0:
                gems.append(Gem(enemy.x, enemy.y, enemy.xp_value))
                enemies.remove(enemy)
                enemies_killed += 1
    
    mortar_flash = 25
    mortar_phase = 0
    
    mortar_impact_effects = []
    for _ in range(60):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0, mortar_radius)
        mortar_impact_effects.append({
            'x': mortar_target_x + math.cos(angle) * dist,
            'y': mortar_target_y + math.sin(angle) * dist,
            'life': 35 + random.randint(0, 20),
            'vx': math.cos(angle) * random.uniform(2, 12),
            'vy': math.sin(angle) * random.uniform(2, 12) - 5,
            'size': random.randint(3, 12)
        })
    mortar_shells.clear()

# ============ MRLS STRIKE ============
def call_mrls_strike(target_x, target_y):
    global mrls_active, mrls_target_x, mrls_target_y, mrls_cooldown
    global mrls_rockets, mrls_explosions, mrls_phase, mrls_fire_timer
    global mrls_rockets_fired, mrls_warning_timer, mrls_flash
    
    if mrls_cooldown > 0 or not is_ability_unlocked('mrls'):
        return False
    
    try:
        mrls_active = True
        mrls_target_x = target_x
        mrls_target_y = target_y
        mrls_rockets = []
        mrls_explosions = []
        mrls_phase = 1
        mrls_fire_timer = 0
        mrls_rockets_fired = 0
        mrls_warning_timer = 40
        mrls_flash = 0
        
        for i in range(mrls_total_rockets):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0, 250)
            target_x_pos = target_x + math.cos(angle) * dist
            target_y_pos = target_y + math.sin(angle) * dist
            
            start_x = target_x_pos + random.uniform(-150, 150)
            start_y = -50 - random.randint(0, 100)
            
            mrls_rockets.append({
                'x': start_x,
                'y': start_y,
                'target_x': target_x_pos,
                'target_y': target_y_pos,
                'speed': random.uniform(20, 30),
                'trail': [],
                'active': True,
                'impacted': False
            })
        
        mrls_cooldown = int(mrls_max_cooldown * (1.0 - (level - 1) * BASE_STATS['cooldown_reduction']))
        mrls_cooldown = max(mrls_cooldown, 140)
        
        return True
    except:
        mrls_active = False
        return False

def execute_mrls_strike():
    global mrls_phase, mrls_rockets_fired, mrls_warning_timer, mrls_flash
    global mrls_rockets, mrls_explosions, mrls_active
    global enemies, gems, enemies_killed
    
    if not mrls_active:
        return
    
    try:
        if mrls_warning_timer > 0:
            mrls_warning_timer -= 1
        
        if mrls_phase == 1:
            all_impacted = True
            
            for rocket in mrls_rockets:
                if rocket['active'] and not rocket['impacted']:
                    all_impacted = False
                    
                    dx = rocket['target_x'] - rocket['x']
                    dy = rocket['target_y'] - rocket['y']
                    dist = math.hypot(dx, dy)
                    
                    if dist > 5:
                        speed = rocket['speed']
                        rocket['x'] += (dx / dist) * speed
                        rocket['y'] += (dy / dist) * speed * 0.5 - 0.1
                        
                        rocket['trail'].append({'x': rocket['x'], 'y': rocket['y'], 'life': 10})
                        if len(rocket['trail']) > 15:
                            rocket['trail'].pop(0)
                    else:
                        rocket['impacted'] = True
                        rocket['active'] = False
                        create_mrls_explosion(rocket['target_x'], rocket['target_y'])
            
            for rocket in mrls_rockets:
                for trail in rocket['trail'][:]:
                    trail['life'] -= 1
                    if trail['life'] <= 0:
                        rocket['trail'].remove(trail)
            
            if all_impacted:
                mrls_phase = 2
                mrls_flash = 30
        
        elif mrls_phase == 2:
            if mrls_flash > 0:
                mrls_flash -= 1
            
            for explosion in mrls_explosions[:]:
                explosion['life'] -= 1
                explosion['x'] += explosion['vx']
                explosion['y'] += explosion['vy']
                explosion['vy'] += 0.2
                if explosion['life'] <= 0:
                    mrls_explosions.remove(explosion)
            
            if len(mrls_explosions) == 0 and mrls_flash == 0:
                mrls_active = False
                mrls_phase = 0
                mrls_rockets.clear()
    
    except:
        mrls_active = False
        mrls_phase = 0
        mrls_rockets.clear()
        mrls_explosions.clear()

def create_mrls_explosion(x, y):
    global mrls_explosions, mrls_flash
    global enemies, gems, enemies_killed
    
    try:
        explosion_radius = 120 + level * 2
        damage = 60 + level * 5
        
        for enemy in enemies[:]:
            dist = distance(x, y, enemy.x, enemy.y)
            if dist < explosion_radius:
                dmg_mult = 1 - (dist / explosion_radius) * 0.3
                enemy.hp -= damage * dmg_mult
                
                if dist > 0:
                    enemy.knockback_x = (enemy.x - x) / dist * 35
                    enemy.knockback_y = (enemy.y - y) / dist * 35
                
                enemy.hit_timer = 20
                if enemy.hp <= 0:
                    gems.append(Gem(enemy.x, enemy.y, enemy.xp_value))
                    enemies.remove(enemy)
                    enemies_killed += 1
        
        mrls_flash = 20
        
        for _ in range(30):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0, explosion_radius * 0.8)
            mrls_explosions.append({
                'x': x + math.cos(angle) * dist,
                'y': y + math.sin(angle) * dist,
                'life': 20 + random.randint(0, 15),
                'vx': math.cos(angle) * random.uniform(2, 10),
                'vy': math.sin(angle) * random.uniform(2, 10) - 3,
                'size': random.randint(3, 14),
                'color': random.choice([(255, 200, 50), (255, 150, 20), (255, 100, 0), (255, 255, 100)])
            })
    except:
        pass

# ============ LEVEL SYSTEM - NON-PAUSING ============

def apply_level_up():
    global player_max_health, player_health, player_speed, level, xp, level_up_notifications
    
    player_max_health += BASE_STATS['health_bonus']
    player_health = min(player_health + BASE_STATS['health_bonus'], player_max_health)
    player_speed += BASE_STATS['speed_bonus']
    
    notification = {
        'text': f"⬆ LEVEL {level}!",
        'subtext': f"HP +{BASE_STATS['health_bonus']} | Speed +{BASE_STATS['speed_bonus']:.1f}",
        'timer': 120
    }
    
    new_abilities = []
    for ability, unlock_level in UNLOCK_LEVELS.items():
        if level == unlock_level:
            names = {'strafe': '✈️ STRAFE RUN', 'mortar': '💥 MORTAR STRIKE', 'mrls': '🚀 MRLS STRIKE'}
            new_abilities.append(names.get(ability, ability))
    
    if new_abilities:
        notification['subtext'] += f" | 🎯 {', '.join(new_abilities)} UNLOCKED!"
    
    level_up_notifications.append(notification)

# ============ DRAW FUNCTIONS ============

def draw_map():
    grid_size = 100
    start_x = int(camera_x - SCREEN_WIDTH//2 / zoom_level)
    end_x = int(camera_x + SCREEN_WIDTH//2 / zoom_level)
    start_y = int(camera_y - SCREEN_HEIGHT//2 / zoom_level)
    end_y = int(camera_y + SCREEN_HEIGHT//2 / zoom_level)
    
    for x in range(start_x - start_x % grid_size, end_x + grid_size, grid_size):
        screen_x, _ = world_to_screen(x, 0)
        if 0 <= screen_x <= SCREEN_WIDTH:
            pygame.draw.line(screen, (30, 35, 45), (screen_x, 0), (screen_x, SCREEN_HEIGHT), 1)
    
    for y in range(start_y - start_y % grid_size, end_y + grid_size, grid_size):
        _, screen_y = world_to_screen(0, y)
        if 0 <= screen_y <= SCREEN_HEIGHT:
            pygame.draw.line(screen, (30, 35, 45), (0, screen_y), (SCREEN_WIDTH, screen_y), 1)

def draw_aiming_reticle():
    if not aiming_mode: return
    
    screen_x, screen_y = world_to_screen(aim_x, aim_y)
    
    pygame.draw.circle(screen, WHITE, (int(screen_x), int(screen_y)), 40, 3)
    pygame.draw.circle(screen, RED, (int(screen_x), int(screen_y)), 40, 2)
    pygame.draw.line(screen, WHITE, (screen_x - 60, screen_y), (screen_x - 20, screen_y), 3)
    pygame.draw.line(screen, WHITE, (screen_x + 20, screen_y), (screen_x + 60, screen_y), 3)
    pygame.draw.line(screen, WHITE, (screen_x, screen_y - 60), (screen_x, screen_y - 20), 3)
    pygame.draw.line(screen, WHITE, (screen_x, screen_y + 20), (screen_x, screen_y + 60), 3)
    pygame.draw.circle(screen, RED, (int(screen_x), int(screen_y)), 5)
    
    if aiming_ability == "strafe":
        label = medium_font.render("✈️ STRAFE", True, YELLOW)
        screen.blit(label, (screen_x - 50, screen_y - 90))
        start_x = screen_x + math.cos(strafe_angle + math.pi/2) * strafe_range * zoom_level
        start_y = screen_y + math.sin(strafe_angle + math.pi/2) * strafe_range * zoom_level
        end_x = screen_x + math.cos(strafe_angle - math.pi/2) * strafe_range * zoom_level
        end_y = screen_y + math.sin(strafe_angle - math.pi/2) * strafe_range * zoom_level
        pygame.draw.line(screen, (255, 200, 0), (start_x, start_y), (end_x, end_y), 3)
    elif aiming_ability == "mortar":
        label = medium_font.render("💥 MORTAR", True, ORANGE)
        screen.blit(label, (screen_x - 50, screen_y - 90))
        pygame.draw.circle(screen, (255, 100, 0, 50), (int(screen_x), int(screen_y)), int(mortar_radius * zoom_level), 2)
    elif aiming_ability == "mrls":
        label = medium_font.render("🚀 MRLS", True, CYAN)
        screen.blit(label, (screen_x - 50, screen_y - 90))
        pygame.draw.circle(screen, (200, 200, 255, 50), (int(screen_x), int(screen_y)), int(250 * zoom_level), 3)
    
    instr = small_font.render("Click to aim | Right-click or press ESC to cancel", True, WHITE)
    screen.blit(instr, (SCREEN_WIDTH//2 - instr.get_width()//2, 10))
    
    cancel_button.x = SCREEN_WIDTH//2 - 50
    cancel_button.y = SCREEN_HEIGHT - 50
    pygame.draw.rect(screen, RED, cancel_button, border_radius=8)
    pygame.draw.rect(screen, WHITE, cancel_button, 2, border_radius=8)
    cancel_text = medium_font.render("CANCEL", True, WHITE)
    screen.blit(cancel_text, (cancel_button.x + 12, cancel_button.y + 8))

def draw_minimap():
    pygame.draw.rect(screen, (20, 20, 30), minimap_rect)
    pygame.draw.rect(screen, (80, 80, 120), minimap_rect, 2)
    
    scale_x = minimap_rect.width / MAP_WIDTH
    scale_y = minimap_rect.height / MAP_HEIGHT
    
    for enemy in enemies:
        mx = minimap_rect.x + enemy.x * scale_x
        my = minimap_rect.y + enemy.y * scale_y
        if enemy.type in ['leviathan', 'titan', 'colossus']:
            color = (255, 0, 0)
            size = 4
        elif enemy.type in ['behemoth', 'juggernaut']:
            color = (200, 100, 0)
            size = 3
        else:
            color = RED
            size = 2
        pygame.draw.circle(screen, color, (int(mx), int(my)), size)
    
    for gem in gems:
        mx = minimap_rect.x + gem.x * scale_x
        my = minimap_rect.y + gem.y * scale_y
        pygame.draw.circle(screen, YELLOW, (int(mx), int(my)), 1)
    
    px = minimap_rect.x + player_x * scale_x
    py = minimap_rect.y + player_y * scale_y
    pygame.draw.circle(screen, GREEN, (int(px), int(py)), 4)
    
    view_left = (camera_x - SCREEN_WIDTH//2 / zoom_level) * scale_x + minimap_rect.x
    view_top = (camera_y - SCREEN_HEIGHT//2 / zoom_level) * scale_y + minimap_rect.y
    view_width = (SCREEN_WIDTH / zoom_level) * scale_x
    view_height = (SCREEN_HEIGHT / zoom_level) * scale_y
    pygame.draw.rect(screen, WHITE, (view_left, view_top, view_width, view_height), 1)

def draw_ability_buttons():
    # Strafe
    unlocked = is_ability_unlocked('strafe')
    color = GRAY if (strafe_cooldown > 0 or not unlocked) else (200, 150, 50)
    pygame.draw.rect(screen, color, strafe_button, border_radius=12)
    pygame.draw.rect(screen, WHITE, strafe_button, 3, border_radius=12)
    icon = "✈️" if unlocked else "🔒"
    icon_text = medium_font.render(icon, True, WHITE)
    screen.blit(icon_text, (strafe_button.x + 15, strafe_button.y + 10))
    label = small_font.render("STRAFE", True, WHITE)
    screen.blit(label, (strafe_button.x + 8, strafe_button.y + 55))
    if strafe_cooldown > 0 and unlocked:
        ratio = strafe_cooldown / strafe_max_cooldown
        pygame.draw.rect(screen, (0, 0, 0, 150), (strafe_button.x, strafe_button.y, strafe_button.width, strafe_button.height * ratio))
        cd_text = small_font.render(f"{strafe_cooldown//60+1}s", True, WHITE)
        screen.blit(cd_text, (strafe_button.x + 28, strafe_button.y + 30))
    elif not unlocked:
        lock_text = small_font.render(f"Lv{UNLOCK_LEVELS['strafe']}", True, WHITE)
        screen.blit(lock_text, (strafe_button.x + 20, strafe_button.y + 30))
    
    # Mortar
    unlocked = is_ability_unlocked('mortar')
    color = GRAY if (mortar_cooldown > 0 or not unlocked) else (200, 80, 50)
    pygame.draw.rect(screen, color, mortar_button, border_radius=12)
    pygame.draw.rect(screen, WHITE, mortar_button, 3, border_radius=12)
    icon = "💥" if unlocked else "🔒"
    icon_text = medium_font.render(icon, True, WHITE)
    screen.blit(icon_text, (mortar_button.x + 15, mortar_button.y + 10))
    label = small_font.render("MORTAR", True, WHITE)
    screen.blit(label, (mortar_button.x + 5, mortar_button.y + 55))
    if mortar_cooldown > 0 and unlocked:
        ratio = mortar_cooldown / mortar_max_cooldown
        pygame.draw.rect(screen, (0, 0, 0, 150), (mortar_button.x, mortar_button.y, mortar_button.width, mortar_button.height * ratio))
        cd_text = small_font.render(f"{mortar_cooldown//60+1}s", True, WHITE)
        screen.blit(cd_text, (mortar_button.x + 28, mortar_button.y + 30))
    elif not unlocked:
        lock_text = small_font.render(f"Lv{UNLOCK_LEVELS['mortar']}", True, WHITE)
        screen.blit(lock_text, (mortar_button.x + 20, mortar_button.y + 30))
    
    # MRLS
    unlocked = is_ability_unlocked('mrls')
    color = GRAY if (mrls_cooldown > 0 or not unlocked) else (200, 100, 50)
    pygame.draw.rect(screen, color, mrls_button, border_radius=12)
    pygame.draw.rect(screen, WHITE, mrls_button, 3, border_radius=12)
    icon = "🚀" if unlocked else "🔒"
    icon_text = medium_font.render(icon, True, WHITE)
    screen.blit(icon_text, (mrls_button.x + 15, mrls_button.y + 10))
    label = small_font.render("MRLS", True, WHITE)
    screen.blit(label, (mrls_button.x + 10, mrls_button.y + 55))
    if mrls_cooldown > 0 and unlocked:
        ratio = mrls_cooldown / mrls_max_cooldown
        pygame.draw.rect(screen, (0, 0, 0, 150), (mrls_button.x, mrls_button.y, mrls_button.width, mrls_button.height * ratio))
        cd_text = small_font.render(f"{mrls_cooldown//60+1}s", True, WHITE)
        screen.blit(cd_text, (mrls_button.x + 28, mrls_button.y + 30))
    elif not unlocked:
        lock_text = small_font.render(f"Lv{UNLOCK_LEVELS['mrls']}", True, WHITE)
        screen.blit(lock_text, (mrls_button.x + 20, mrls_button.y + 30))

def draw_zoom_buttons():
    pygame.draw.rect(screen, DARK_GRAY, zoom_in_button, border_radius=10)
    pygame.draw.rect(screen, WHITE, zoom_in_button, 2, border_radius=10)
    zoom_text = big_font.render("+", True, WHITE)
    screen.blit(zoom_text, (zoom_in_button.x + 14, zoom_in_button.y + 5))
    
    pygame.draw.rect(screen, DARK_GRAY, zoom_out_button, border_radius=10)
    pygame.draw.rect(screen, WHITE, zoom_out_button, 2, border_radius=10)
    zoom_text = big_font.render("-", True, WHITE)
    screen.blit(zoom_text, (zoom_out_button.x + 18, zoom_out_button.y + 5))
    
    zoom_percent = int(zoom_level * 100)
    zoom_indicator = small_font.render(f"{zoom_percent}%", True, WHITE)
    screen.blit(zoom_indicator, (SCREEN_WIDTH - 70, 240))

def draw_mrls():
    if not mrls_active:
        return
    
    try:
        if mrls_warning_timer > 0:
            screen_x, screen_y = world_to_screen(mrls_target_x, mrls_target_y)
            pulse = math.sin(mrls_warning_timer * 0.3) * 0.3 + 0.7
            radius = 250 * zoom_level * pulse
            
            pygame.draw.circle(screen, (255, 50, 50), (int(screen_x), int(screen_y)), int(radius), 3)
            
            if mrls_warning_timer > 25:
                warning = big_font.render("⚠️ MRLS INCOMING!", True, RED)
                screen.blit(warning, (screen_x - warning.get_width()//2, screen_y - 100))
            else:
                warning = big_font.render("💥 IMPACT!", True, YELLOW)
                screen.blit(warning, (screen_x - warning.get_width()//2, screen_y - 100))
        
        for rocket in mrls_rockets:
            for trail in rocket['trail']:
                screen_x, screen_y = world_to_screen(trail['x'], trail['y'])
                alpha = trail['life'] / 10
                size = int(5 * alpha * zoom_level)
                if size > 0:
                    pygame.draw.circle(screen, (255, 200, 100), (int(screen_x), int(screen_y)), size)
            
            if rocket['active'] and not rocket['impacted']:
                screen_x, screen_y = world_to_screen(rocket['x'], rocket['y'])
                size = int(10 * zoom_level)
                
                pygame.draw.circle(screen, (255, 200, 50), (int(screen_x), int(screen_y)), size + 4)
                pygame.draw.circle(screen, (255, 220, 80), (int(screen_x), int(screen_y)), size)
                pygame.draw.circle(screen, (255, 180, 20), (int(screen_x), int(screen_y)), int(size * 0.6))
                
                flame_x = screen_x - 6 * zoom_level
                flame_y = screen_y + 6 * zoom_level
                pygame.draw.circle(screen, (255, 100, 0), (int(flame_x), int(flame_y)), int(size * 0.9))
                pygame.draw.circle(screen, (255, 200, 50), (int(flame_x), int(flame_y)), int(size * 0.5))
                pygame.draw.circle(screen, (255, 255, 200), (int(flame_x), int(flame_y)), int(size * 0.3))
        
        for explosion in mrls_explosions:
            screen_x, screen_y = world_to_screen(explosion['x'], explosion['y'])
            alpha = explosion['life'] / 20
            size = int(explosion['size'] * alpha * zoom_level)
            if size > 0:
                color = explosion['color']
                pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), size)
                if size > 2:
                    pygame.draw.circle(screen, (255, 255, 200), (int(screen_x), int(screen_y)), int(size * 1.3))
        
        if mrls_flash > 0:
            screen_x, screen_y = world_to_screen(mrls_target_x, mrls_target_y)
            flash_radius = mrls_flash * 10 * zoom_level
            pygame.draw.circle(screen, (255, 255, 200), (int(screen_x), int(screen_y)), int(flash_radius))
            pygame.draw.circle(screen, (255, 255, 255), (int(screen_x), int(screen_y)), int(flash_radius * 0.4))
    except:
        pass

def draw_strafe():
    if not strafe_active:
        return
    
    try:
        center_x, center_y = world_to_screen(strafe_x, strafe_y)
        
        start_x = center_x + math.cos(strafe_angle + math.pi/2) * strafe_range * zoom_level
        start_y = center_y + math.sin(strafe_angle + math.pi/2) * strafe_range * zoom_level
        end_x = center_x + math.cos(strafe_angle - math.pi/2) * strafe_range * zoom_level
        end_y = center_y + math.sin(strafe_angle - math.pi/2) * strafe_range * zoom_level
        
        for i in range(3):
            alpha = 100 - i * 30
            width = 5 - i
            if width > 0:
                pygame.draw.line(screen, (255, 200, 50, alpha), (start_x, start_y), (end_x, end_y), width)
        pygame.draw.line(screen, (255, 255, 100), (start_x, start_y), (end_x, end_y), 2)
        
        for i in range(-2, 3):
            progress = 0.5 + i * 0.1
            x = start_x + (end_x - start_x) * progress
            y = start_y + (end_y - start_y) * progress
            
            dir_angle = strafe_angle
            size = 10 * zoom_level
            for j in range(3):
                a = dir_angle + j * 0.3 - 0.3
                end_x2 = x + math.cos(a) * size
                end_y2 = y + math.sin(a) * size
                pygame.draw.line(screen, (255, 200, 50), (x, y), (end_x2, end_y2), 2)
        
        for bullet in strafe_bullets:
            screen_x, screen_y = world_to_screen(bullet['x'], bullet['y'])
            alpha = bullet['life'] / 20
            size = int(4 * alpha * zoom_level)
            if size > 0:
                pygame.draw.circle(screen, (255, 255, 200), (int(screen_x), int(screen_y)), size)
                pygame.draw.circle(screen, (255, 200, 50), (int(screen_x), int(screen_y)), size // 2)
        
        for particle in strafe_particles:
            screen_x, screen_y = world_to_screen(particle['x'], particle['y'])
            alpha = particle['life'] / 30
            color = (255, int(particle['color'][1] * alpha), 0)
            size = int(particle['size'] * alpha * zoom_level)
            if size > 0:
                pygame.draw.circle(screen, color, (int(screen_x), int(screen_y)), size)
                if size > 2:
                    pygame.draw.circle(screen, (255, 255, 200), (int(screen_x), int(screen_y)), size * 2, 1)
    
    except:
        pass

def draw_level_up_notifications():
    """Draw non-pausing level up notifications"""
    y_offset = 0
    for notification in level_up_notifications[:]:
        # Fade out
        alpha = min(1.0, notification['timer'] / 30)
        
        # Background
        text = huge_font.render(notification['text'], True, YELLOW)
        text.set_alpha(int(255 * alpha))
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 100 + y_offset))
        
        subtext = medium_font.render(notification['subtext'], True, WHITE)
        subtext.set_alpha(int(200 * alpha))
        screen.blit(subtext, (SCREEN_WIDTH//2 - subtext.get_width()//2, 160 + y_offset))
        
        # Update timer
        notification['timer'] -= 1
        if notification['timer'] <= 0:
            level_up_notifications.remove(notification)
        y_offset += 80

def draw_game_over():
    screen.fill(BLACK)
    text1 = huge_font.render("💀 KIA - EVAC FAILED", True, RED)
    text2 = medium_font.render(f"Level: {level}  Kills: {enemies_killed}  Time: {game_time//60}s", True, WHITE)
    text3 = small_font.render("Press SPACE or Click to respawn", True, WHITE)
    
    screen.blit(text1, (SCREEN_WIDTH//2 - text1.get_width()//2, SCREEN_HEIGHT//2 - 100))
    screen.blit(text2, (SCREEN_WIDTH//2 - text2.get_width()//2, SCREEN_HEIGHT//2 - 20))
    screen.blit(text3, (SCREEN_WIDTH//2 - text3.get_width()//2, SCREEN_HEIGHT//2 + 40))
    pygame.display.flip()

def game_over_screen():
    draw_game_over()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True
        clock.tick(30)

def reset_game():
    global player_x, player_y, player_health, player_max_health, level, xp, xp_to_next
    global enemies, gems, camera_x, camera_y, zoom_level
    global strafe_cooldown, strafe_active, mortar_cooldown, mortar_phase
    global mrls_cooldown, mrls_active, aiming_mode, player_speed
    global strafe_particles, mortar_impact_effects, enemy_spawn_timer
    global mrls_phase, mrls_rockets, mrls_explosions, mrls_warning_timer
    global strafe_bullets, enemies_killed, game_time, level_up_notifications
    
    player_x, player_y = MAP_WIDTH // 2, MAP_HEIGHT // 2
    player_health = 100
    player_max_health = 100
    player_speed = 4.0
    level = 1
    xp = 0
    xp_to_next = 30
    enemies.clear()
    gems.clear()
    enemies_killed = 0
    game_time = 0
    level_up_notifications.clear()
    camera_x, camera_y = player_x, player_y
    zoom_level = 1.0
    strafe_cooldown = 0
    strafe_active = False
    strafe_bullets = []
    mortar_cooldown = 0
    mortar_phase = 0
    mrls_cooldown = 0
    mrls_active = False
    mrls_phase = 0
    mrls_rockets.clear()
    mrls_explosions.clear()
    mrls_warning_timer = 0
    aiming_mode = False
    strafe_particles.clear()
    mortar_impact_effects.clear()
    enemy_spawn_timer = 0

# ============ KEYBOARD HELP TEXT ============
def draw_keyboard_help():
    help_text = small_font.render("WASD: Move | 1: Strafe | 2: Mortar | 3: MRLS | ESC: Cancel | R: Restart", True, (150, 150, 150))
    screen.blit(help_text, (SCREEN_WIDTH//2 - help_text.get_width()//2, SCREEN_HEIGHT - 30))

# ============ MAIN GAME LOOP ============

running = True

while running:
    # ============ EVENT HANDLING ============
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Keyboard events
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                keys_pressed['up'] = True
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                keys_pressed['down'] = True
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                keys_pressed['left'] = True
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                keys_pressed['right'] = True
            
            if event.key == pygame.K_1 and is_ability_unlocked('strafe'): 
                start_aiming("strafe")
            if event.key == pygame.K_2 and is_ability_unlocked('mortar'): 
                start_aiming("mortar")
            if event.key == pygame.K_3 and is_ability_unlocked('mrls'): 
                start_aiming("mrls")
            if event.key == pygame.K_ESCAPE: 
                cancel_aim()
            if event.key == pygame.K_r: 
                reset_game()
            if event.key == pygame.K_SPACE and xp >= xp_to_next:
                xp = 0
                level += 1
                apply_level_up()
            if event.key in [pygame.K_PLUS, pygame.K_EQUALS]: 
                zoom_level = min(zoom_level + zoom_speed, max_zoom)
            if event.key == pygame.K_MINUS: 
                zoom_level = max(zoom_level - zoom_speed, min_zoom)
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                keys_pressed['up'] = False
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                keys_pressed['down'] = False
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                keys_pressed['left'] = False
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                keys_pressed['right'] = False
        
        # Mouse events
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            
            # Right click to cancel aiming
            if event.button == 3 and aiming_mode:
                cancel_aim()
                continue
            
            if event.button == 4:  # Scroll up
                zoom_level = min(zoom_level + zoom_speed, max_zoom)
                continue
            if event.button == 5:  # Scroll down
                zoom_level = max(zoom_level - zoom_speed, min_zoom)
                continue
            
            if xp >= xp_to_next and upgrade_button.collidepoint(x, y):
                xp = 0
                level += 1
                apply_level_up()
                continue
            
            if strafe_button.collidepoint(x, y):
                if aiming_mode: 
                    confirm_aim()
                elif is_ability_unlocked('strafe'): 
                    start_aiming("strafe")
                continue
            
            if mortar_button.collidepoint(x, y):
                if aiming_mode: 
                    confirm_aim()
                elif is_ability_unlocked('mortar'): 
                    start_aiming("mortar")
                continue
            
            if mrls_button.collidepoint(x, y):
                if aiming_mode: 
                    confirm_aim()
                elif is_ability_unlocked('mrls'): 
                    start_aiming("mrls")
                continue
            
            if aiming_mode and cancel_button.collidepoint(x, y):
                cancel_aim()
                continue
            
            if zoom_in_button.collidepoint(x, y):
                zoom_level = min(zoom_level + zoom_speed, max_zoom)
                continue
            if zoom_out_button.collidepoint(x, y):
                zoom_level = max(zoom_level - zoom_speed, min_zoom)
                continue
            
            if aiming_mode:
                aim_x, aim_y = screen_to_world(x, y)
                aim_x = clamp(aim_x, 0, MAP_WIDTH)
                aim_y = clamp(aim_y, 0, MAP_HEIGHT)
                confirm_aim()
            else:
                mouse_held = True
        
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_held = False
        
        if event.type == pygame.MOUSEMOTION:
            if aiming_mode and mouse_held:
                aim_x, aim_y = screen_to_world(event.pos[0], event.pos[1])
                aim_x = clamp(aim_x, 0, MAP_WIDTH)
                aim_y = clamp(aim_y, 0, MAP_HEIGHT)
    
    # ============ UPDATE GAME TIME ============
    game_time += 1
    
    # ============ PLAYER MOVEMENT (Keyboard) ============
    move_mult = 0.6 if aiming_mode else 1.0
    
    dx, dy = 0, 0
    if keys_pressed['up']: dy -= 1
    if keys_pressed['down']: dy += 1
    if keys_pressed['left']: dx -= 1
    if keys_pressed['right']: dx += 1
    
    if dx != 0 or dy != 0:
        length = math.hypot(dx, dy)
        dx /= length
        dy /= length
        player_x += dx * player_speed * move_mult
        player_y += dy * player_speed * move_mult
    
    player_x = clamp(player_x, 0, MAP_WIDTH)
    player_y = clamp(player_y, 0, MAP_HEIGHT)
    
    camera_x += (player_x - camera_x) * 0.08
    camera_y += (player_y - camera_y) * 0.08
    
    # ============ UPDATE ABILITIES ============
    if strafe_cooldown > 0: 
        strafe_cooldown -= 1
    if mortar_cooldown > 0: 
        mortar_cooldown -= 1
    if mrls_cooldown > 0: 
        mrls_cooldown -= 1
    
    # Strafe
    if strafe_active:
        execute_strafing_run()
    
    # Mortar
    if mortar_phase == 1:
        mortar_impact_timer -= 1
        for shell in mortar_shells[:]:
            shell['y'] += shell['speed']
            if shell['y'] > shell['target_y']:
                mortar_shells.remove(shell)
        if mortar_impact_timer <= 0:
            execute_mortar_strike()
    
    if mortar_flash > 0: 
        mortar_flash -= 1
    
    for effect in mortar_impact_effects[:]:
        effect['x'] += effect['vx']
        effect['y'] += effect['vy']
        effect['vy'] += 0.2
        effect['life'] -= 1
        if effect['life'] <= 0:
            mortar_impact_effects.remove(effect)
    
    # MRLS
    if mrls_active:
        try:
            execute_mrls_strike()
        except:
            mrls_active = False
            mrls_phase = 0
            mrls_rockets.clear()
            mrls_explosions.clear()
    
    # ============ SPAWN ENEMIES ============
    enemy_spawn_timer += 1
    
    current_delay = max(10, enemy_spawn_delay - game_time // 300)
    
    if enemy_spawn_timer >= current_delay and len(enemies) < max_enemies:
        enemy_spawn_timer = 0
        spawn_enemy()
    
    # ============ UPDATE ENEMIES ============
    for enemy in enemies[:]:
        enemy.move_towards_player(player_x, player_y)
        
        if distance(enemy.x, enemy.y, player_x, player_y) < (enemy.size + player_size) / 2 and enemy.attack_cooldown == 0:
            player_health -= enemy.damage
            enemy.attack_cooldown = 40
            
            dx = enemy.x - player_x
            dy = enemy.y - player_y
            dist = math.hypot(dx, dy)
            if dist > 0:
                enemy.knockback_x = (dx / dist) * 20
                enemy.knockback_y = (dy / dist) * 20
            
            if player_health <= 0:
                if game_over_screen():
                    reset_game()
                else:
                    running = False
                break
    
    # ============ UPDATE GEMS ============
    for gem in gems[:]:
        gem.update(player_x, player_y)
        if gem.rect.colliderect(pygame.Rect(player_x - 12, player_y - 12, 24, 24)):
            xp += gem.value
            gems.remove(gem)
            if xp >= xp_to_next:
                xp = 0
                level += 1
                apply_level_up()
    
    # ============ DRAW EVERYTHING ============
    screen.fill(BLACK)
    draw_map()
    
    # Draw strafe
    draw_strafe()
    
    # Draw mortar
    if mortar_phase == 1:
        screen_x, screen_y = world_to_screen(mortar_target_x, mortar_target_y)
        pygame.draw.circle(screen, RED, (int(screen_x), int(screen_y)), int(18 * zoom_level), 3)
        warning = big_font.render("⚠️ INCOMING!", True, RED)
        screen.blit(warning, (screen_x - 80, screen_y - 80))
        
        for shell in mortar_shells:
            shell_x, shell_y = world_to_screen(shell['x'], shell['y'])
            pygame.draw.circle(screen, ORANGE, (int(shell_x), int(shell_y)), int(12 * zoom_level))
    
    if mortar_flash > 0:
        screen_x, screen_y = world_to_screen(mortar_target_x, mortar_target_y)
        flash_radius = mortar_radius * zoom_level * (mortar_flash / 25)
        pygame.draw.circle(screen, (255, 200, 100), (int(screen_x), int(screen_y)), int(flash_radius))
        pygame.draw.circle(screen, WHITE, (int(screen_x), int(screen_y)), int(flash_radius), int(5 * zoom_level))
    
    for effect in mortar_impact_effects:
        screen_x, screen_y = world_to_screen(effect['x'], effect['y'])
        alpha = effect['life'] / 35
        size = int(effect['size'] * alpha * zoom_level)
        if size > 0:
            pygame.draw.circle(screen, (255, int(150 * alpha), int(50 * alpha)), (int(screen_x), int(screen_y)), size)
    
    # Draw MRLS
    draw_mrls()
    
    # Draw enemies
    for enemy in enemies:
        enemy.draw(screen, camera_x, camera_y, zoom_level)
    
    # Draw gems
    for gem in gems:
        gem.draw(screen, camera_x, camera_y, zoom_level)
    
    # Draw player
    screen_x, screen_y = world_to_screen(player_x, player_y)
    pygame.draw.circle(screen, (50, 150, 50), (int(screen_x), int(screen_y)), int(16 * zoom_level))
    pygame.draw.circle(screen, GREEN, (int(screen_x), int(screen_y)), int(12 * zoom_level))
    pygame.draw.circle(screen, WHITE, (int(screen_x + 7 * zoom_level), int(screen_y + 7 * zoom_level)), int(4 * zoom_level))
    pygame.draw.circle(screen, WHITE, (int(screen_x + 17 * zoom_level), int(screen_y + 7 * zoom_level)), int(4 * zoom_level))
    
    # Draw aiming reticle
    draw_aiming_reticle()
    
    # ============ UI ============
    if not aiming_mode:
        # Health
        bar_width, bar_height = int(200 * ui_scale), int(20 * ui_scale)
        pygame.draw.rect(screen, RED, (int(15 * ui_scale), int(15 * ui_scale), bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (int(15 * ui_scale), int(15 * ui_scale), bar_width * (player_health/player_max_health), bar_height))
        health_text = small_font.render(f"HP: {int(player_health)}/{int(player_max_health)}", True, WHITE)
        screen.blit(health_text, (int(20 * ui_scale), int(17 * ui_scale)))
        
        # XP
        bar_width, bar_height = int(200 * ui_scale), int(16 * ui_scale)
        pygame.draw.rect(screen, (30, 30, 50), (int(15 * ui_scale), int(40 * ui_scale), bar_width, bar_height))
        pygame.draw.rect(screen, BLUE, (int(15 * ui_scale), int(40 * ui_scale), bar_width * (xp/xp_to_next if xp_to_next > 0 else 0), bar_height))
        xp_text = small_font.render(f"XP: {int(xp)}/{int(xp_to_next)}", True, WHITE)
        screen.blit(xp_text, (int(20 * ui_scale), int(42 * ui_scale)))
        
        # Info - No waves, just time and kills
        time_seconds = game_time // 60
        info1 = small_font.render(f"Level {level}  Kills: {enemies_killed}  Time: {time_seconds}s", True, WHITE)
        info2 = small_font.render(f"Enemies: {len(enemies)}/{max_enemies}", True, WHITE)
        screen.blit(info1, (int(230 * ui_scale), int(15 * ui_scale)))
        screen.blit(info2, (int(230 * ui_scale), int(35 * ui_scale)))
        
        # Ability status - top right
        y_pos = int(15 * ui_scale)
        if is_ability_unlocked('strafe'):
            status = "READY" if strafe_cooldown == 0 else f"{strafe_cooldown//60+1}s"
            color = GREEN if strafe_cooldown == 0 else GRAY
            text = small_font.render(f"✈️ {status}", True, color)
            screen.blit(text, (SCREEN_WIDTH - text.get_width() - int(15 * ui_scale), y_pos))
            y_pos += int(22 * ui_scale)
        
        if is_ability_unlocked('mortar'):
            status = "READY" if mortar_cooldown == 0 else f"{mortar_cooldown//60+1}s"
            color = GREEN if mortar_cooldown == 0 else GRAY
            text = small_font.render(f"💥 {status}", True, color)
            screen.blit(text, (SCREEN_WIDTH - text.get_width() - int(15 * ui_scale), y_pos))
            y_pos += int(22 * ui_scale)
        
        if is_ability_unlocked('mrls'):
            status = "READY" if mrls_cooldown == 0 else f"{mrls_cooldown//60+1}s"
            color = GREEN if mrls_cooldown == 0 else GRAY
            text = small_font.render(f"🚀 {status}", True, color)
            screen.blit(text, (SCREEN_WIDTH - text.get_width() - int(15 * ui_scale), y_pos))
        
        draw_minimap()
        draw_zoom_buttons()
        draw_ability_buttons()
        
        # Keyboard help
        draw_keyboard_help()
        
        # Upgrade button - only show if enough XP
        if xp >= xp_to_next:
            upgrade_button.x = SCREEN_WIDTH//2 - int(80 * ui_scale)
            upgrade_button.y = SCREEN_HEIGHT - int(80 * ui_scale)
            upgrade_button.width = int(160 * ui_scale)
            upgrade_button.height = int(50 * ui_scale)
            pygame.draw.rect(screen, YELLOW, upgrade_button, border_radius=12)
            pygame.draw.rect(screen, WHITE, upgrade_button, 3, border_radius=12)
            upgrade_label = medium_font.render("⬆ UPGRADE", True, BLACK)
            screen.blit(upgrade_label, (upgrade_button.x + int(20 * ui_scale), upgrade_button.y + int(12 * ui_scale)))
    
    # Draw level up notifications (non-pausing)
    draw_level_up_notifications()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()