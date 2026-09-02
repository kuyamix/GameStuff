import pygame
import math
from constants import PURPLE, BLACK, WHITE
from entities.projectile import Projectile

class Tower:
    def __init__(self, x, y, tower_cost):
        self.rect = pygame.Rect(x - 20, y - 20, 40, 40)
        self.damage = 25
        self.range = 250
        self.cooldown = 0
        self.max_cooldown = 30
        self.cost = tower_cost
        self.target = None
        self.level = 1
        self.kills = 0
        self.xp = 0
    
    def find_target(self, enemies):
        self.target = None
        closest_distance = self.range
        
        for enemy in enemies:
            distance = math.sqrt((enemy.rect.centerx - self.rect.centerx)**2 + 
                               (enemy.rect.centery - self.rect.centery)**2)
            if distance <= closest_distance:
                closest_distance = distance
                self.target = enemy
    
    def shoot(self, projectiles):
        if self.target and self.cooldown <= 0:
            projectiles.append(Projectile(self.rect.centerx, self.rect.centery, self.target, self.damage, self))
            self.cooldown = self.max_cooldown
    
    def update(self, enemies, projectiles):
        if self.cooldown > 0:
            self.cooldown -= 1
        self.find_target(enemies)
        self.shoot(projectiles)
    
    def draw(self, camera, screen, small_font):
        screen_pos = camera.world_to_screen(self.rect.centerx, self.rect.centery)
        scaled_radius = int(20 * camera.zoom)
        
        # Draw tower
        pygame.draw.circle(screen, PURPLE, screen_pos, scaled_radius)
        pygame.draw.circle(screen, BLACK, screen_pos, scaled_radius, max(1, int(3 * camera.zoom)))
        
        # Draw level indicator
        if camera.zoom > 0.7:
            level_text = small_font.render(str(self.level), True, WHITE)
            text_rect = level_text.get_rect(center=screen_pos)
            screen.blit(level_text, text_rect)