import pygame
import math
from constants import YELLOW, ORANGE

class Projectile:
    def __init__(self, x, y, target, damage, tower):
        self.x = x
        self.y = y
        self.target = target
        self.speed = 8
        self.damage = damage
        self.active = True
        self.tower = tower
    
    def update(self):
        if not self.target or self.target.health <= 0:
            self.active = False
            return
        
        dx = self.target.rect.centerx - self.x
        dy = self.target.rect.centery - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < 15:
            self.target.take_damage(self.damage)
            if self.target.health <= 0:
                if self.tower:
                    self.tower.kills += 1
                    if self.tower.kills % 10 == 0:
                        self.tower.level += 1
                        self.tower.damage += 5
                        self.tower.range += 10
            self.active = False
        else:
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
    
    def draw(self, camera, screen):
        screen_pos = camera.world_to_screen(self.x, self.y)
        scaled_radius = int(6 * camera.zoom)
        pygame.draw.circle(screen, YELLOW, screen_pos, scaled_radius)
        pygame.draw.circle(screen, ORANGE, screen_pos, max(1, int(3 * camera.zoom)))