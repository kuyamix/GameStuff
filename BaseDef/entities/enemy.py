import pygame
import math
from constants import RED, BLACK, GREEN

class Enemy:
    def __init__(self, start_x, start_y, base, wave):
        self.rect = pygame.Rect(start_x - 12, start_y - 12, 24, 24)
        self.base = base
        self.health = 50 + (wave - 1) * 15
        self.max_health = self.health
        self.speed = 1.5 + (wave - 1) * 0.15
        self.damage = 8
        self.reached_base = False
        self.wave = wave
    
    def move_toward_base(self):
        dx = self.base.rect.centerx - self.rect.centerx
        dy = self.base.rect.centery - self.rect.centery
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance < 40:
            self.reached_base = True
            self.base.take_damage(self.damage)
        else:
            self.rect.x += (dx / distance) * self.speed
            self.rect.y += (dy / distance) * self.speed
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0
    
    def update(self):
        self.move_toward_base()
    
    def draw(self, camera, screen):
        screen_pos = camera.world_to_screen(self.rect.centerx, self.rect.centery)
        scaled_radius = int(12 * camera.zoom)
        
        # Draw enemy
        pygame.draw.circle(screen, RED, screen_pos, scaled_radius)
        pygame.draw.circle(screen, BLACK, screen_pos, scaled_radius, max(1, int(2 * camera.zoom)))
        
        # Draw health bar
        if camera.zoom > 0.5:
            bar_width = int(24 * camera.zoom)
            bar_height = max(3, int(5 * camera.zoom))
            bar_x = screen_pos[0] - bar_width // 2
            bar_y = screen_pos[1] - scaled_radius - bar_height - 3
            health_percentage = self.health / self.max_health
            pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, GREEN, (bar_x, bar_y, int(bar_width * health_percentage), bar_height))
            pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 1)