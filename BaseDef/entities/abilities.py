import pygame
import math
from constants import RED, ORANGE, YELLOW, WHITE, CYAN, GRAY

class ArtilleryStrike:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 120
        self.damage = 100
        self.duration = 90
        self.explosion_duration = 40
        self.exploded = False
        self.active = True
        self.warning_flash = 0
    
    def update(self, enemies):
        if not self.exploded:
            self.duration -= 1
            self.warning_flash += 1
            if self.duration <= 0:
                self.explode(enemies)
        else:
            self.explosion_duration -= 1
            if self.explosion_duration <= 0:
                self.active = False
    
    def explode(self, enemies):
        self.exploded = True
        for enemy in enemies[:]:
            distance = math.sqrt((enemy.rect.centerx - self.x)**2 + 
                               (enemy.rect.centery - self.y)**2)
            if distance <= self.radius:
                enemy.take_damage(self.damage)
                if enemy.health <= 0:
                    enemies.remove(enemy)
    
    def draw(self, camera, screen):
        screen_pos = camera.world_to_screen(self.x, self.y)
        scaled_radius = int(self.radius * camera.zoom)
        
        if not self.exploded:
            pygame.draw.circle(screen, RED, screen_pos, scaled_radius, max(1, int(2 * camera.zoom)))
            line_length = int(20 * camera.zoom)
            pygame.draw.line(screen, RED, (screen_pos[0] - line_length, screen_pos[1]), 
                           (screen_pos[0] + line_length, screen_pos[1]), max(1, int(2 * camera.zoom)))
            pygame.draw.line(screen, RED, (screen_pos[0], screen_pos[1] - line_length), 
                           (screen_pos[0], screen_pos[1] + line_length), max(1, int(2 * camera.zoom)))
        else:
            explosion_radius = scaled_radius * (1 - self.explosion_duration / 40)
            pygame.draw.circle(screen, ORANGE, screen_pos, int(explosion_radius))
            pygame.draw.circle(screen, YELLOW, screen_pos, int(explosion_radius * 0.6))
            pygame.draw.circle(screen, WHITE, screen_pos, int(explosion_radius * 0.3))


class StrafingRun:
    def __init__(self, target_x, target_y):
        self.target_x = target_x
        self.target_y = target_y
        self.damage = 25
        self.width = 80
        self.length = 300
        self.duration = 45
        self.strafe_duration = 60
        self.active = True
        self.planes_arrived = False
        self.warning_flash = 0
        self.plane1_x = target_x - 400
        self.plane1_y = target_y
        self.plane2_x = target_x - 450
        self.plane2_y = target_y - 30
        self.plane_speed = 15
        self.start_x = target_x - 400
        self.end_x = target_x + self.length
    
    def update(self, enemies):
        if not self.planes_arrived:
            self.duration -= 1
            self.warning_flash += 1
            if self.duration <= 0:
                self.planes_arrived = True
        else:
            self.plane1_x += self.plane_speed
            self.plane2_x += self.plane_speed
            self.strafe_duration -= 1
            
            if self.strafe_duration % 8 == 0:
                self.damage_enemies_in_path(enemies)
            
            if self.plane1_x > self.end_x + 200:
                self.active = False
    
    def damage_enemies_in_path(self, enemies):
        if self.plane1_x < self.start_x - 50 or self.plane1_x > self.end_x:
            return
            
        for enemy in enemies[:]:
            enemy_x = enemy.rect.centerx
            enemy_y = enemy.rect.centery
            
            if (self.start_x <= enemy_x <= self.end_x and 
                abs(enemy_y - self.target_y) < self.width / 2):
                enemy.take_damage(self.damage)
                if enemy.health <= 0:
                    enemies.remove(enemy)
    
    def draw(self, camera, screen):
        if not self.planes_arrived:
            start_screen = camera.world_to_screen(self.start_x, self.target_y)
            end_screen = camera.world_to_screen(self.end_x, self.target_y)
            pygame.draw.line(screen, CYAN, start_screen, end_screen, max(1, int(2 * camera.zoom)))
            
            arrow_spacing = max(50, int(100 / camera.zoom))
            for x in range(self.start_x, self.end_x, arrow_spacing):
                screen_pos = camera.world_to_screen(x, self.target_y)
                arrow_size = max(10, int(20 * camera.zoom))
                pygame.draw.polygon(screen, CYAN, [
                    screen_pos,
                    (screen_pos[0] + arrow_size, screen_pos[1] - arrow_size//2),
                    (screen_pos[0] + arrow_size, screen_pos[1] + arrow_size//2)
                ])
        else:
            plane1_screen = camera.world_to_screen(self.plane1_x, self.plane1_y)
            plane2_screen = camera.world_to_screen(self.plane2_x, self.plane2_y)
            self._draw_plane(plane1_screen[0], plane1_screen[1], camera.zoom, screen)
            self._draw_plane(plane2_screen[0], plane2_screen[1], camera.zoom, screen)
            
            if self.strafe_duration % 5 == 0:
                tracer_length = min(300, self.end_x - self.plane1_x)
                for x in range(int(self.plane1_x), min(int(self.plane1_x) + tracer_length, self.end_x), 25):
                    start_screen = camera.world_to_screen(x, self.plane1_y)
                    end_screen = camera.world_to_screen(x + 10, self.plane1_y + self.width/2)
                    pygame.draw.line(screen, YELLOW, start_screen, end_screen, 1)
                    end_screen = camera.world_to_screen(x + 10, self.plane1_y - self.width/2)
                    pygame.draw.line(screen, YELLOW, start_screen, end_screen, 1)
    
    def _draw_plane(self, x, y, zoom, screen):
        scale = max(0.5, zoom)
        pygame.draw.polygon(screen, GRAY, [
            (x, y),
            (x - 20 * scale, y - 10 * scale),
            (x - 20 * scale, y + 10 * scale)
        ])
        pygame.draw.polygon(screen, GRAY, [
            (x - 10 * scale, y),
            (x - 30 * scale, y - 25 * scale),
            (x - 30 * scale, y + 25 * scale)
        ])
        pygame.draw.circle(screen, CYAN, (int(x - 5 * scale), int(y)), max(1, int(3 * scale)))