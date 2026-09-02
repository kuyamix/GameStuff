import pygame
from constants import BLUE, BLACK, WHITE, GREEN, RED

class Base:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 80, 80)
        self.health = 400
        self.max_health = 400
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0
    
    def draw(self, camera, screen):
        screen_pos = camera.world_to_screen(self.rect.x, self.rect.y)
        scaled_width = int(self.rect.width * camera.zoom)
        scaled_height = int(self.rect.height * camera.zoom)
        
        # Draw base
        screen_rect = pygame.Rect(screen_pos[0], screen_pos[1], scaled_width, scaled_height)
        pygame.draw.rect(screen, BLUE, screen_rect)
        pygame.draw.rect(screen, BLACK, screen_rect, max(1, int(3 * camera.zoom)))
        
        # Draw base symbol
        center_x = screen_pos[0] + scaled_width // 2
        center_y = screen_pos[1] + scaled_height // 2
        pygame.draw.line(screen, WHITE, (center_x - 15 * camera.zoom, center_y), 
                        (center_x + 15 * camera.zoom, center_y), max(1, int(3 * camera.zoom)))
        pygame.draw.line(screen, WHITE, (center_x, center_y - 15 * camera.zoom), 
                        (center_x, center_y + 15 * camera.zoom), max(1, int(3 * camera.zoom)))
        
        # Draw health bar
        bar_width = scaled_width
        bar_height = max(4, int(10 * camera.zoom))
        bar_x = screen_pos[0]
        bar_y = screen_pos[1] - bar_height - 5
        health_percentage = self.health / self.max_health
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, int(bar_width * health_percentage), bar_height))
        pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 1)