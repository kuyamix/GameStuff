import pygame
import math
import random
from settings import *

class EnemyStructure:
    def __init__(self, x, y, structure_type="hive"):
        self.x = x
        self.y = y
        self.type = structure_type
        self.alive = True
        
        if structure_type == "hive":
            self.health = 500
            self.max_health = 500
            self.radius = 40
            self.color = (150, 100, 50)
            self.spawn_rate = 3.0
            self.spawn_type = "scavenger"
            self.score_value = 500
        elif structure_type == "nest":
            self.health = 750
            self.max_health = 750
            self.radius = 50
            self.color = (100, 150, 50)
            self.spawn_rate = 2.5
            self.spawn_type = "warrior"
            self.score_value = 750
        elif structure_type == "command":
            self.health = 1000
            self.max_health = 1000
            self.radius = 60
            self.color = (150, 50, 50)
            self.spawn_rate = 2.0
            self.spawn_type = "spewer"
            self.score_value = 1000
        
        self.spawn_timer = random.uniform(1.0, self.spawn_rate)
        self.flash_timer = 0
        self.pulse_timer = 0
        self.exploding = False
        self.explosion_timer = 0
        self.explosion_duration = 2.0
        
    def update(self, dt, current_time):
        if not self.alive:
            return None
            
        self.flash_timer = max(0, self.flash_timer - dt)
        self.pulse_timer += dt
        
        if not self.exploding:
            self.spawn_timer -= dt
            if self.spawn_timer <= 0:
                self.spawn_timer = self.spawn_rate
                return self.spawn_enemy()
        else:
            self.explosion_timer -= dt
            if self.explosion_timer <= 0:
                self.alive = False
        
        return None
    
    def spawn_enemy(self):
        from enemies import Bug
        
        angle = random.uniform(0, math.pi * 2)
        distance = self.radius + 20
        spawn_x = self.x + math.cos(angle) * distance
        spawn_y = self.y + math.sin(angle) * distance
        
        return Bug(spawn_x, spawn_y, self.spawn_type)
    
    def take_damage(self, damage):
        if not self.alive:
            return
            
        self.health -= damage
        self.flash_timer = 0.1
        
        if self.health <= 0 and not self.exploding:
            self.exploding = True
            self.explosion_timer = self.explosion_duration
            self.health = 0
    
    def draw(self, screen, camera_offset=(0, 0)):
        if not self.alive:
            return
        
        draw_x = self.x + camera_offset[0]
        draw_y = self.y + camera_offset[1]
        
        pulse = math.sin(self.pulse_timer * 3) * 3
        
        if self.exploding:
            if int(self.explosion_timer * 10) % 2 == 0:
                color = WHITE
            else:
                color = RED
        else:
            color = RED if self.flash_timer > 0 else self.color
        
        pygame.draw.circle(screen, color, (int(draw_x), int(draw_y)), 
                          self.radius + pulse)
        
        if self.type == "hive":
            for i in range(6):
                angle = (i / 6) * math.pi * 2
                hole_x = draw_x + math.cos(angle) * (self.radius * 0.5)
                hole_y = draw_y + math.sin(angle) * (self.radius * 0.5)
                pygame.draw.circle(screen, (80, 50, 30), 
                                 (int(hole_x), int(hole_y)), 10)
        elif self.type == "nest":
            for i in range(8):
                angle = (i / 8) * math.pi * 2
                spike_x = draw_x + math.cos(angle) * (self.radius + 10)
                spike_y = draw_y + math.sin(angle) * (self.radius + 10)
                pygame.draw.line(screen, (100, 80, 40), 
                               (draw_x, draw_y), (spike_x, spike_y), 3)
        elif self.type == "command":
            pygame.draw.line(screen, (100, 100, 100), 
                           (draw_x, draw_y), (draw_x, draw_y - self.radius - 20), 3)
            pygame.draw.circle(screen, RED, 
                             (int(draw_x), int(draw_y - self.radius - 20)), 8)
        
        pygame.draw.circle(screen, DARK_GRAY, (int(draw_x), int(draw_y)), 
                          self.radius + pulse, 3)
        
        bar_width = self.radius * 2
        bar_height = 6
        bar_x = draw_x - bar_width // 2
        bar_y = draw_y - self.radius - 30
        health_percent = self.health / self.max_health
        
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, 
                        (bar_x, bar_y, bar_width * health_percent, bar_height))

class ExplosiveBarrel:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 50
        self.radius = 12
        self.alive = True
        self.color = (200, 50, 50)
        self.flash_timer = 0
        
    def take_damage(self, damage):
        self.health -= damage
        self.flash_timer = 0.1
        if self.health <= 0:
            self.alive = False
            return True
        return False
    
    def draw(self, screen, camera_offset=(0, 0)):
        if not self.alive:
            return
            
        draw_x = self.x + camera_offset[0]
        draw_y = self.y + camera_offset[1]
        
        color = RED if self.flash_timer > 0 else self.color
        pygame.draw.circle(screen, color, (int(draw_x), int(draw_y)), self.radius)
        pygame.draw.circle(screen, (150, 30, 30), (int(draw_x), int(draw_y)), 
                          self.radius, 2)
        pygame.draw.line(screen, YELLOW, 
                        (draw_x - self.radius, draw_y), 
                        (draw_x + self.radius, draw_y), 2)

class Rock:
    """Terrain obstacle - VISIBLE and properly rendered."""
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = (120, 120, 120)
        self.outline_color = (80, 80, 80)
        
    def draw(self, screen, camera_offset=(0, 0)):
        draw_x = self.x + camera_offset[0]
        draw_y = self.y + camera_offset[1]
        
        # Draw shadow
        pygame.draw.circle(screen, (40, 40, 40), 
                          (int(draw_x + 3), int(draw_y + 3)), self.radius)
        
        # Draw main rock
        pygame.draw.circle(screen, self.color, 
                          (int(draw_x), int(draw_y)), self.radius)
        
        # Draw outline for visibility
        pygame.draw.circle(screen, self.outline_color, 
                          (int(draw_x), int(draw_y)), self.radius, 3)
        
        # Draw texture details
        for i in range(3):
            detail_x = draw_x + (i - 1) * self.radius * 0.4
            detail_y = draw_y + (i % 2) * self.radius * 0.3
            pygame.draw.circle(screen, (100, 100, 100), 
                             (int(detail_x), int(detail_y)), self.radius * 0.2)

class SupplyCrate:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 30
        self.size = 15
        self.alive = True
        self.color = (150, 120, 50)
        self.flash_timer = 0
        self.contents = random.choice(['ammo', 'health', 'grenade'])
        
    def take_damage(self, damage):
        self.health -= damage
        self.flash_timer = 0.1
        if self.health <= 0:
            self.alive = False
            return True
        return False
    
    def draw(self, screen, camera_offset=(0, 0)):
        if not self.alive:
            return
            
        draw_x = self.x + camera_offset[0]
        draw_y = self.y + camera_offset[1]
        
        color = RED if self.flash_timer > 0 else self.color
        
        pygame.draw.rect(screen, color, 
                        (draw_x - self.size, draw_y - self.size, 
                         self.size * 2, self.size * 2))
        pygame.draw.rect(screen, (100, 80, 30), 
                        (draw_x - self.size, draw_y - self.size, 
                         self.size * 2, self.size * 2), 2)
        
        pygame.draw.line(screen, (100, 80, 30), 
                        (draw_x - self.size, draw_y - self.size), 
                        (draw_x + self.size, draw_y + self.size), 2)
        pygame.draw.line(screen, (100, 80, 30), 
                        (draw_x - self.size, draw_y + self.size), 
                        (draw_x + self.size, draw_y - self.size), 2)