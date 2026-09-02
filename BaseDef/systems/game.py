import pygame
import math
import random
from constants import *
from systems.camera import Camera
from entities.base import Base
from entities.tower import Tower
from entities.enemy import Enemy
from entities.abilities import ArtilleryStrike, StrafingRun
from ui.hud import draw_ui

class Game:
    def __init__(self, screen, font, small_font, large_font, title_font, ui_font, small_bold_font):
        self.screen = screen
        self.font = font
        self.small_font = small_font
        self.large_font = large_font
        self.title_font = title_font
        self.ui_font = ui_font
        self.small_bold_font = small_bold_font
        
        self.camera = Camera()
        self.base = Base(WORLD_WIDTH // 2 - 40, WORLD_HEIGHT // 2 - 40)
        self.camera.center_on(self.base.rect.centerx, self.base.rect.centery)
        
        self.towers = []
        self.enemies = []
        self.projectiles = []
        self.artillery_strikes = []
        self.strafing_runs = []
        
        self.gold = 300
        self.wave = 1
        self.horde_size = 10
        self.spawn_timer = 0
        self.spawn_delay = 15
        self.wave_in_progress = False
        self.wave_delay = 600
        self.wave_timer = self.wave_delay
        self.wave_started_message_timer = 0
        
        self.placing_tower = False
        self.tower_preview_pos = None
        self.artillery_mode = False
        self.strafe_mode = False
        self.game_over = False
        self.kills = 0
        self.artillery_cost = ARTILLERY_COST
        self.strafe_cost = STRAFE_COST
    
    def start_wave(self):
        if not self.wave_in_progress and not self.game_over:
            self.wave_in_progress = True
            self.horde_size = 10 + (self.wave - 1) * 8
            self.spawn_timer = 0
            self.spawn_delay = max(10, 15 - (self.wave - 1) * 0.5)
            self.wave_started_message_timer = 60
    
    def spawn_horde(self):
        horde_spawn_size = min(3, self.horde_size)
        
        for _ in range(horde_spawn_size):
            side = random.randint(0, 3)
            if side == 0:
                x = random.randint(0, WORLD_WIDTH)
                y = -30
            elif side == 1:
                x = WORLD_WIDTH + 30
                y = random.randint(0, WORLD_HEIGHT)
            elif side == 2:
                x = random.randint(0, WORLD_WIDTH)
                y = WORLD_HEIGHT + 30
            else:
                x = -30
                y = random.randint(0, WORLD_HEIGHT)
            
            enemy = Enemy(x, y, self.base, self.wave)
            self.enemies.append(enemy)
        
        self.horde_size -= horde_spawn_size
    
    def call_artillery(self, x, y):
        if self.gold >= self.artillery_cost and not self.game_over:
            self.artillery_strikes.append(ArtilleryStrike(x, y))
            self.gold -= self.artillery_cost
            return True
        return False
    
    def call_strafing_run(self, x, y):
        if self.gold >= self.strafe_cost and not self.game_over:
            self.strafing_runs.append(StrafingRun(x, y))
            self.gold -= self.strafe_cost
            return True
        return False
    
    def update(self):
        if self.game_over:
            return
        
        # Camera movement
        keys = pygame.key.get_pressed()
        camera_speed = 10
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.camera.move(-camera_speed, 0)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.camera.move(camera_speed, 0)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.camera.move(0, -camera_speed)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.camera.move(0, camera_speed)
        
        # Wave management
        if not self.wave_in_progress:
            self.wave_timer -= 1
            if self.wave_timer <= 0:
                self.start_wave()
        else:
            if self.horde_size > 0:
                self.spawn_timer -= 1
                if self.spawn_timer <= 0:
                    self.spawn_horde()
                    self.spawn_timer = self.spawn_delay
            elif len(self.enemies) == 0:
                self.wave_in_progress = False
                self.wave += 1
                self.wave_timer = self.wave_delay
                self.gold += 100 + self.wave * 20
        
        if self.wave_started_message_timer > 0:
            self.wave_started_message_timer -= 1
        
        # Update towers
        for tower in self.towers:
            tower.update(self.enemies, self.projectiles)
        
        # Update projectiles
        for projectile in self.projectiles[:]:
            projectile.update()
            if not projectile.active:
                self.projectiles.remove(projectile)
        
        if len(self.projectiles) > MAX_PROJECTILES:
            self.projectiles = self.projectiles[:MAX_PROJECTILES]
        
        # Update artillery strikes
        for strike in self.artillery_strikes[:]:
            strike.update(self.enemies)
            if not strike.active:
                self.artillery_strikes.remove(strike)
        
        # Update strafing runs
        for run in self.strafing_runs[:]:
            run.update(self.enemies)
            if not run.active:
                self.strafing_runs.remove(run)
        
        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update()
            if enemy.reached_base or enemy.health <= 0:
                if enemy.health <= 0:
                    self.gold += 20
                    self.kills += 1
                self.enemies.remove(enemy)
        
        if self.base.health <= 0:
            self.game_over = True
    
    def draw(self):
        # Draw background
        self.screen.fill(DARK_GREEN)
        
        # Draw grid
        self._draw_grid()
        
        # Draw world border
        border_points = [
            self.camera.world_to_screen(0, 0),
            self.camera.world_to_screen(WORLD_WIDTH, 0),
            self.camera.world_to_screen(WORLD_WIDTH, WORLD_HEIGHT),
            self.camera.world_to_screen(0, WORLD_HEIGHT)
        ]
        pygame.draw.lines(self.screen, BROWN, True, border_points, 3)
        
        # Draw all entities
        self.base.draw(self.camera, self.screen)
        
        for tower in self.towers:
            tower.draw(self.camera, self.screen, self.small_font)
        
        for projectile in self.projectiles:
            projectile.draw(self.camera, self.screen)
        
        for enemy in self.enemies:
            enemy.draw(self.camera, self.screen)
        
        for strike in self.artillery_strikes:
            strike.draw(self.camera, self.screen)
        
        for run in self.strafing_runs:
            run.draw(self.camera, self.screen)
        
        # Draw previews
        self._draw_previews()
        
        # Draw UI
        draw_ui(self.screen, self, self.font, self.small_font, self.large_font, 
                self.title_font, self.ui_font, self.small_bold_font)
    
    def _draw_grid(self):
        grid_spacing = 100
        start_x = max(0, int(self.camera.x // grid_spacing) * grid_spacing)
        end_x = min(WORLD_WIDTH, int((self.camera.x + SCREEN_WIDTH / self.camera.zoom) // grid_spacing + 1) * grid_spacing)
        start_y = max(0, int(self.camera.y // grid_spacing) * grid_spacing)
        end_y = min(WORLD_HEIGHT, int((self.camera.y + SCREEN_HEIGHT / self.camera.zoom) // grid_spacing + 1) * grid_spacing)
        
        for x in range(start_x, end_x + grid_spacing, grid_spacing):
            screen_pos = self.camera.world_to_screen(x, 0)
            pygame.draw.line(self.screen, (0, 80, 0), (screen_pos[0], 0), (screen_pos[0], SCREEN_HEIGHT), 1)
        for y in range(start_y, end_y + grid_spacing, grid_spacing):
            screen_pos = self.camera.world_to_screen(0, y)
            pygame.draw.line(self.screen, (0, 80, 0), (0, screen_pos[1]), (SCREEN_WIDTH, screen_pos[1]), 1)
    
    def _draw_previews(self):
        if not self.tower_preview_pos:
            return
        
        world_pos = self.camera.screen_to_world(*self.tower_preview_pos)
        
        if self.artillery_mode and not self.game_over:
            screen_pos = self.camera.world_to_screen(world_pos[0], world_pos[1])
            scaled_radius = int(120 * self.camera.zoom)
            pygame.draw.circle(self.screen, RED, screen_pos, scaled_radius, 2)
            line_length = int(20 * self.camera.zoom)
            pygame.draw.line(self.screen, RED, (screen_pos[0] - line_length, screen_pos[1]), 
                           (screen_pos[0] + line_length, screen_pos[1]), 2)
            pygame.draw.line(self.screen, RED, (screen_pos[0], screen_pos[1] - line_length), 
                           (screen_pos[0], screen_pos[1] + line_length), 2)
        
        if self.strafe_mode and not self.game_over:
            start_x = world_pos[0] - 400
            end_x = world_pos[0] + 300
            start_screen = self.camera.world_to_screen(start_x, world_pos[1])
            end_screen = self.camera.world_to_screen(end_x, world_pos[1])
            pygame.draw.line(self.screen, CYAN, start_screen, end_screen, 2)
            width = int(40 * self.camera.zoom)
            pygame.draw.line(self.screen, CYAN, (start_screen[0], start_screen[1] - width), 
                           (end_screen[0], end_screen[1] - width), 1)
            pygame.draw.line(self.screen, CYAN, (start_screen[0], start_screen[1] + width), 
                           (end_screen[0], end_screen[1] + width), 1)
        
        if self.placing_tower and not self.artillery_mode and not self.strafe_mode:
            screen_pos = self.camera.world_to_screen(world_pos[0], world_pos[1])
            color = GREEN if self.can_place_tower(world_pos[0], world_pos[1]) else RED
            scaled_radius = int(20 * self.camera.zoom)
            pygame.draw.circle(self.screen, color, screen_pos, scaled_radius)
            pygame.draw.circle(self.screen, BLACK, screen_pos, scaled_radius, max(1, int(3 * self.camera.zoom)))
            range_radius = int(250 * self.camera.zoom)
            range_surface = pygame.Surface((range_radius*2, range_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(range_surface, (128, 128, 128, 64), (range_radius, range_radius), range_radius)
            self.screen.blit(range_surface, (screen_pos[0] - range_radius, screen_pos[1] - range_radius))
            pygame.draw.circle(self.screen, GRAY, screen_pos, range_radius, 1)
        
        # Crosshair
        if self.tower_preview_pos and not self.game_over:
            mx, my = self.tower_preview_pos
            pygame.draw.circle(self.screen, WHITE, (mx, my), 8, 1)
            pygame.draw.line(self.screen, WHITE, (mx - 14, my), (mx - 5, my), 1)
            pygame.draw.line(self.screen, WHITE, (mx + 5, my), (mx + 14, my), 1)
            pygame.draw.line(self.screen, WHITE, (mx, my - 14), (mx, my - 5), 1)
            pygame.draw.line(self.screen, WHITE, (mx, my + 5), (mx, my + 14), 1)
    
    def can_place_tower(self, x, y):
        if x < 30 or x > WORLD_WIDTH - 30 or y < 30 or y > WORLD_HEIGHT - 30:
            return False
        
        distance_to_base = math.sqrt((x - self.base.rect.centerx)**2 + 
                                    (y - self.base.rect.centery)**2)
        if distance_to_base < 150:
            return False
        
        new_rect = pygame.Rect(x - 20, y - 20, 40, 40)
        for tower in self.towers:
            if new_rect.colliderect(tower.rect):
                return False
        
        return True
    
    def place_tower(self, x, y):
        if self.gold >= TOWER_COST and self.can_place_tower(x, y):
            self.towers.append(Tower(x, y, TOWER_COST))
            self.gold -= TOWER_COST
            return True
        return False