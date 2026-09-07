import random
import math
import pygame
from config import *
from utils import distance, clamp

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
        dx, dy = px - self.x, py - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            if self.knockback_x or self.knockback_y:
                self.x += self.knockback_x * 0.5
                self.y += self.knockback_y * 0.5
                self.knockback_x *= 0.9
                self.knockback_y *= 0.9
                if abs(self.knockback_x) < 0.1: self.knockback_x = 0
                if abs(self.knockback_y) < 0.1: self.knockback_y = 0
            else:
                speed = self.speed * (0.8 if self.type in ['heavy', 'juggernaut', 'behemoth', 'colossus', 'titan', 'leviathan'] else 1.0)
                self.x += (dx / dist) * speed
                self.y += (dy / dist) * speed
        self.rect.x, self.rect.y = self.x - self.size//2, self.y - self.size//2
        if self.hit_timer > 0: self.hit_timer -= 1
        if self.attack_cooldown > 0: self.attack_cooldown -= 1
        if dist > 0: self.angle = math.atan2(dy, dx)
    
    def draw(self, screen, cx, cy, zoom):
        sx = (self.x - cx) * zoom + SCREEN_WIDTH//2
        sy = (self.y - cy) * zoom + SCREEN_HEIGHT//2
        size = self.size * zoom
        if sx < -size or sx > SCREEN_WIDTH + size or sy < -size or sy > SCREEN_HEIGHT + size:
            return
        
        # Health bar
        if self.hp < self.max_hp:
            ratio = max(0, self.hp / self.max_hp)
            pygame.draw.rect(screen, RED, (sx - size/2, sy - size/2 - 10*zoom, size, 4*zoom))
            pygame.draw.rect(screen, GREEN, (sx - size/2, sy - size/2 - 10*zoom, size * ratio, 4*zoom))
        
        color = WHITE if self.hit_timer > 0 else self.color
        # Simplified drawing
        if self.type in ["tank", "heavy"]:
            pygame.draw.rect(screen, color, (sx - size/2, sy - size/2, size, size))
        elif self.type == "fast":
            pts = [(sx + math.cos(self.angle) * size/2, sy + math.sin(self.angle) * size/2),
                   (sx + math.cos(self.angle + 2.5) * size/2, sy + math.sin(self.angle + 2.5) * size/2),
                   (sx + math.cos(self.angle - 2.5) * size/2, sy + math.sin(self.angle - 2.5) * size/2)]
            pygame.draw.polygon(screen, color, pts)
        else:
            pygame.draw.circle(screen, color, (int(sx), int(sy)), int(size/2))

class Gem:
    def __init__(self, x, y, value):
        self.x, self.y, self.value = x, y, value
        self.rect = pygame.Rect(x - 8, y - 8, 16, 16)
        self.bob_timer = random.randint(0, 100)
        self.pull_speed = 0
    
    def update(self, px, py):
        self.bob_timer += 0.1
        dx, dy = px - self.x, py - self.y
        dist = math.hypot(dx, dy)
        if dist < 200:
            self.pull_speed = min(self.pull_speed + 0.1, 5)
            if dist > 0:
                self.x += (dx / dist) * self.pull_speed
                self.y += (dy / dist) * self.pull_speed
        else:
            self.pull_speed = max(self.pull_speed - 0.05, 0)
        self.rect.x, self.rect.y = self.x - 8, self.y - 8 + math.sin(self.bob_timer) * 2
    
    def draw(self, screen, cx, cy, zoom):
        sx = (self.x - cx) * zoom + SCREEN_WIDTH//2
        sy = (self.y - cy) * zoom + SCREEN_HEIGHT//2
        size = (8 + math.sin(self.bob_timer) * 1.5) * zoom
        if sx < -size or sx > SCREEN_WIDTH + size or sy < -size or sy > SCREEN_HEIGHT + size:
            return
        pygame.draw.circle(screen, YELLOW, (int(sx), int(sy)), int(size))
        pygame.draw.circle(screen, ORANGE, (int(sx) - 2, int(sy) - 2), int(size * 0.5))

def spawn_enemy(game):
    time_s = game.game_time // 60
    types = ['grunt']
    if time_s > 10: types.append('fast')
    if time_s > 20: types.append('tank')
    if time_s > 35: types.append('heavy')
    if time_s > 50: types.append('elite')
    if time_s > 70: types.append('juggernaut')
    if time_s > 90: types.append('behemoth')
    if time_s > 120: types.append('colossus')
    if time_s > 160: types.append('titan')
    if time_s > 200: types.append('leviathan')
    
    # Weighted selection
    weights = {'grunt': 50, 'fast': 40, 'tank': 30, 'heavy': 20, 'elite': 15,
               'juggernaut': 10, 'behemoth': 8, 'colossus': 5, 'titan': 3, 'leviathan': 2}
    available = [t for t in types if t in weights]
    enemy_type = random.choices(available, [weights[t] for t in available])[0] if available else 'grunt'
    
    side = random.randint(0, 3)
    if side == 0: x, y = random.randint(0, MAP_WIDTH), -30
    elif side == 1: x, y = random.randint(0, MAP_WIDTH), MAP_HEIGHT + 30
    elif side == 2: x, y = -30, random.randint(0, MAP_HEIGHT)
    else: x, y = MAP_WIDTH + 30, random.randint(0, MAP_HEIGHT)
    
    stats = ENEMY_TYPES[enemy_type].copy()
    scale = 1 + (time_s / 60) * 0.15
    stats['hp'] = int(stats['hp'] * scale)
    stats['speed'] *= (1 + (time_s / 60) * 0.03)
    stats['xp'] = int(stats['xp'] * scale)
    stats['damage'] = int(stats['damage'] * scale)
    
    game.enemies.append(Enemy(x, y, stats['speed'], stats['hp'], stats['size'], 
                              stats['color'], stats['xp'], enemy_type, stats['damage']))