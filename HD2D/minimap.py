import pygame
import math
from settings import *

class Minimap:
    def __init__(self, map_width, map_height, minimap_width=200, minimap_height=150):
        self.map_width = map_width
        self.map_height = map_height
        self.minimap_width = minimap_width
        self.minimap_height = minimap_height
        
        self.x = SCREEN_WIDTH - minimap_width - 10
        self.y = 10
        
        self.scale_x = minimap_width / map_width
        self.scale_y = minimap_height / map_height
        
        self.visible = True
        
    def world_to_minimap(self, world_x, world_y):
        minimap_x = self.x + world_x * self.scale_x
        minimap_y = self.y + world_y * self.scale_y
        return (int(minimap_x), int(minimap_y))
    
    def draw(self, screen, player, enemies, structures, camera, turrets=None):
        if not self.visible:
            return
        
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y, self.minimap_width, self.minimap_height))
        pygame.draw.rect(screen, (50, 50, 50), (self.x, self.y, self.minimap_width, self.minimap_height), 2)
        
        for structure in structures:
            if structure.alive:
                minimap_x, minimap_y = self.world_to_minimap(structure.x, structure.y)
                
                if structure.type == "command":
                    color = RED
                elif structure.type == "nest":
                    color = GREEN
                else:
                    color = (150, 100, 50)
                
                pygame.draw.circle(screen, color, (minimap_x, minimap_y), 4)
                
                if structure.type == "command":
                    pygame.draw.circle(screen, RED, (minimap_x, minimap_y), 7, 1)
        
        if turrets:
            for turret in turrets:
                if turret.alive:
                    minimap_x, minimap_y = self.world_to_minimap(turret.x, turret.y)
                    pygame.draw.circle(screen, CYAN, (minimap_x, minimap_y), 2)
        
        for enemy in enemies:
            if enemy.alive:
                minimap_x, minimap_y = self.world_to_minimap(enemy.x, enemy.y)
                pygame.draw.circle(screen, RED, (minimap_x, minimap_y), 1)
        
        minimap_x, minimap_y = self.world_to_minimap(player.x, player.y)
        pygame.draw.circle(screen, BLUE, (minimap_x, minimap_y), 3)
        pygame.draw.circle(screen, WHITE, (minimap_x, minimap_y), 3, 1)
        
        viewport_left = camera.x * self.scale_x + self.x
        viewport_top = camera.y * self.scale_y + self.y
        viewport_width = camera.screen_width * self.scale_x
        viewport_height = camera.screen_height * self.scale_y
        
        pygame.draw.rect(screen, WHITE, 
                        (viewport_left, viewport_top, viewport_width, viewport_height), 1)
    
    def toggle(self):
        self.visible = not self.visible
        return self.visible