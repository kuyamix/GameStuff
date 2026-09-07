import pygame
import math
import random
from settings import *
from structures import EnemyStructure, ExplosiveBarrel, Rock, SupplyCrate
from camera import Camera
from minimap import Minimap

class DestructionMode:
    def __init__(self, game):
        self.game = game
        
        self.map_width = SCREEN_WIDTH * 3
        self.map_height = SCREEN_HEIGHT * 3
        
        self.camera = Camera(self.map_width, self.map_height, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.minimap = Minimap(self.map_width, self.map_height)
        
        self.structures = []
        self.barrels = []
        self.rocks = []
        self.crates = []
        
        self.objective_complete = False
        self.objective_timer = 0
        self.structures_destroyed = 0
        self.total_structures = 0
        
        self.generate_structures()
        self.generate_barrels()
        # self.generate_rocks()  # DISABLED - No invisible walls
        self.generate_crates()
        
    def generate_structures(self):
        self.total_structures = 4 + (self.game.wave_manager.current_wave // 3)
        
        positions = []
        margin = 200
        
        command_x = int(self.map_width * 0.7) + random.randint(-100, 100)
        command_y = int(self.map_height * 0.5) + random.randint(-100, 100)
        command_x = max(margin, min(command_x, self.map_width - margin))
        command_y = max(margin, min(command_y, self.map_height - margin))
        positions.append((command_x, command_y))
        
        for i in range(self.total_structures - 1):
            attempts = 0
            while attempts < 100:
                quadrant = i % 4
                if quadrant == 0:
                    x = random.randint(margin, int(self.map_width * 0.4))
                    y = random.randint(margin, int(self.map_height * 0.4))
                elif quadrant == 1:
                    x = random.randint(int(self.map_width * 0.6), self.map_width - margin)
                    y = random.randint(margin, int(self.map_height * 0.4))
                elif quadrant == 2:
                    x = random.randint(margin, int(self.map_width * 0.4))
                    y = random.randint(int(self.map_height * 0.6), self.map_height - margin)
                else:
                    x = random.randint(int(self.map_width * 0.6), self.map_width - margin)
                    y = random.randint(int(self.map_height * 0.6), self.map_height - margin)
                
                valid = True
                for pos in positions:
                    dist = math.sqrt((x - pos[0])**2 + (y - pos[1])**2)
                    if dist < 500:
                        valid = False
                        break
                
                player_dist = math.sqrt((x - self.map_width//2)**2 + 
                                       (y - self.map_height//2)**2)
                if player_dist < 400:
                    valid = False
                
                if valid:
                    positions.append((x, y))
                    break
                
                attempts += 1
            
            if len(positions) <= i + 1:
                positions.append((
                    random.randint(margin, self.map_width - margin),
                    random.randint(margin, self.map_height - margin)
                ))
        
        for i, (x, y) in enumerate(positions):
            if i == 0:
                structure_type = "command"
            elif i < 3:
                structure_type = "nest"
            else:
                structure_type = "hive"
            
            self.structures.append(EnemyStructure(x, y, structure_type))
    
    def generate_barrels(self):
        num_barrels = random.randint(15, 25)
        
        for _ in range(num_barrels):
            if random.random() < 0.5 and len(self.structures) > 0:
                structure = random.choice(self.structures)
                angle = random.uniform(0, math.pi * 2)
                distance = random.uniform(100, 200)
                x = int(structure.x + math.cos(angle) * distance)
                y = int(structure.y + math.sin(angle) * distance)
            else:
                x = random.randint(50, self.map_width - 50)
                y = random.randint(50, self.map_height - 50)
            
            x = max(50, min(x, self.map_width - 50))
            y = max(50, min(y, self.map_height - 50))
            
            self.barrels.append(ExplosiveBarrel(x, y))
    
    def generate_crates(self):
        num_crates = random.randint(8, 12)
        
        for _ in range(num_crates):
            x = random.randint(100, self.map_width - 100)
            y = random.randint(100, self.map_height - 100)
            self.crates.append(SupplyCrate(x, y))
    
    def update(self, dt):
        if self.game.player.alive:
            self.camera.update(self.game.player.x, self.game.player.y, dt)
        
        for structure in self.structures[:]:
            if not self.camera.is_visible(structure.x, structure.y, margin=200):
                continue
                
            new_enemy = structure.update(dt, self.game.game_time)
            
            if new_enemy and structure.alive and not structure.exploding:
                self.game.enemies.append(new_enemy)
            
            if structure.exploding and not structure.alive:
                self.structures_destroyed += 1
                self.game.score += structure.score_value
                
                self.game.screen_shake.add_shake(20, 0.5)
                self.game.sound_system.play('explosion')
                self.game.particle_system.add_particles(
                    self.game.particle_system.spawn_explosion(
                        structure.x, structure.y, 100
                    )
                )
                
                from effects import ExplosionEffect
                self.game.effects.append(
                    ExplosionEffect(structure.x, structure.y, 0, 100)
                )
                
                self.game.damage_enemies_in_radius(
                    structure.x, structure.y, 150, 200
                )
                
                self.structures.remove(structure)
                
                if len(self.structures) == 0:
                    self.objective_complete = True
                    self.objective_timer = 5.0
        
        for barrel in self.barrels[:]:
            if not barrel.alive:
                self.barrels.remove(barrel)
        
        for crate in self.crates[:]:
            if not crate.alive:
                self.crates.remove(crate)
        
        if self.objective_complete:
            self.objective_timer -= dt
            if self.objective_timer <= 0:
                self.game.victory = True
    
    def check_structure_hits(self, bullet):
        for structure in self.structures:
            if structure.alive and not structure.exploding:
                if self.game.check_collision(
                    bullet.x, bullet.y, bullet.radius,
                    structure.x, structure.y, structure.radius
                ):
                    structure.take_damage(bullet.damage)
                    return True
        
        for barrel in self.barrels[:]:
            if barrel.alive:
                if self.game.check_collision(
                    bullet.x, bullet.y, bullet.radius,
                    barrel.x, barrel.y, barrel.radius
                ):
                    exploded = barrel.take_damage(bullet.damage)
                    if exploded:
                        self.explode_barrel(barrel)
                    return True
        
        for crate in self.crates[:]:
            if crate.alive:
                if self.game.check_collision(
                    bullet.x, bullet.y, bullet.radius,
                    crate.x, crate.y, crate.size
                ):
                    destroyed = crate.take_damage(bullet.damage)
                    if destroyed:
                        self.open_crate(crate)
                    return True
        
        return False
    
    def explode_barrel(self, barrel):
        self.game.screen_shake.add_shake(10, 0.3)
        self.game.sound_system.play('explosion')
        self.game.particle_system.add_particles(
            self.game.particle_system.spawn_explosion(
                barrel.x, barrel.y, 60
            )
        )
        
        from effects import ExplosionEffect
        self.game.effects.append(
            ExplosionEffect(barrel.x, barrel.y, 0, 60)
        )
        
        self.game.damage_enemies_in_radius(
            barrel.x, barrel.y, 80, 100
        )
        
        if self.game.player.alive:
            if self.game.check_collision(
                barrel.x, barrel.y, 0,
                self.game.player.x, self.game.player.y, 80
            ):
                self.game.player.take_damage(30, "self")
        
        for structure in self.structures:
            if structure.alive and not structure.exploding:
                if self.game.check_collision(
                    barrel.x, barrel.y, 0,
                    structure.x, structure.y, 80
                ):
                    structure.take_damage(100)
        
        self.barrels.remove(barrel)
    
    def open_crate(self, crate):
        self.game.sound_system.play('hit_enemy')
        
        if crate.contents == 'ammo':
            if self.game.player.weapon.type != 'laser':
                self.game.player.weapon.ammo = self.game.player.weapon.max_ammo
            self.game.add_damage_number(crate.x, crate.y, "AMMO", YELLOW)
        elif crate.contents == 'health':
            self.game.player.heal(50)
            self.game.add_damage_number(crate.x, crate.y, "+50 HP", GREEN)
        elif crate.contents == 'grenade':
            self.game.player.grenades = min(3, self.game.player.grenades + 1)
            self.game.add_damage_number(crate.x, crate.y, "GRENADE", ORANGE)
        
        self.game.particle_system.add_particles(
            self.game.particle_system.spawn_explosion(crate.x, crate.y, 20)
        )
        
        self.crates.remove(crate)
    
    def draw(self, screen):
        camera_offset = self.camera.get_offset()
        
        for crate in self.crates:
            if self.camera.is_visible(crate.x, crate.y):
                crate.draw(screen, camera_offset)
        
        for barrel in self.barrels:
            if self.camera.is_visible(barrel.x, barrel.y):
                barrel.draw(screen, camera_offset)
        
        for structure in self.structures:
            if self.camera.is_visible(structure.x, structure.y, margin=200):
                structure.draw(screen, camera_offset)
                
                if structure.alive and not structure.exploding:
                    pulse = math.sin(pygame.time.get_ticks() * 0.005) * 5
                    marker_y = structure.y - structure.radius - 40 + pulse
                    
                    pygame.draw.polygon(screen, RED, [
                        (structure.x + camera_offset[0], marker_y + camera_offset[1] - 10),
                        (structure.x + camera_offset[0] - 8, marker_y + camera_offset[1]),
                        (structure.x + camera_offset[0] + 8, marker_y + camera_offset[1])
                    ])
    
    def draw_ui(self, screen):
        self.minimap.draw(
            screen, 
            self.game.player, 
            self.game.enemies, 
            self.structures, 
            self.camera,
            self.game.turrets
        )
        
        font = pygame.font.Font(None, 36)
        
        if not self.objective_complete:
            objective_text = f"DESTROY ENEMY STRUCTURES: {self.structures_destroyed}/{self.total_structures}"
        else:
            objective_text = "OBJECTIVE COMPLETE!"
        
        text = font.render(objective_text, True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        screen.blit(text, text_rect)
        
        icon_y = 60
        icon_x_start = SCREEN_WIDTH // 2 - (self.total_structures * 25) // 2
        
        for i in range(self.total_structures):
            icon_x = icon_x_start + i * 25
            
            if i < self.structures_destroyed:
                pygame.draw.circle(screen, GREEN, (icon_x, icon_y), 8)
                pygame.draw.line(screen, BLACK, 
                               (icon_x - 4, icon_y - 4), 
                               (icon_x + 4, icon_y + 4), 2)
                pygame.draw.line(screen, BLACK, 
                               (icon_x - 4, icon_y + 4), 
                               (icon_x + 4, icon_y - 4), 2)
            else:
                pygame.draw.circle(screen, RED, (icon_x, icon_y), 8, 2)
        
        if len(self.structures) > 0:
            hint_text = font.render("FOLLOW THE RED MARKERS", True, YELLOW)
            hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, 90))
            screen.blit(hint_text, hint_rect)
    
    def draw_off_screen_indicators(self, screen):
        for structure in self.structures:
            if not structure.alive or structure.exploding:
                continue
            
            screen_x, screen_y = self.camera.apply(structure.x, structure.y)
            
            margin = 50
            if (screen_x < -margin or screen_x > SCREEN_WIDTH + margin or
                screen_y < -margin or screen_y > SCREEN_HEIGHT + margin):
                
                angle = math.atan2(structure.y - self.game.player.y,
                                  structure.x - self.game.player.x)
                
                indicator_x = SCREEN_WIDTH // 2 + math.cos(angle) * 300
                indicator_y = SCREEN_HEIGHT // 2 + math.sin(angle) * 200
                
                indicator_x = max(30, min(indicator_x, SCREEN_WIDTH - 30))
                indicator_y = max(30, min(indicator_y, SCREEN_HEIGHT - 30))
                
                arrow_size = 15
                arrow_points = [
                    (indicator_x + math.cos(angle) * arrow_size,
                     indicator_y + math.sin(angle) * arrow_size),
                    (indicator_x + math.cos(angle + 2.5) * arrow_size * 0.6,
                     indicator_y + math.sin(angle + 2.5) * arrow_size * 0.6),
                    (indicator_x + math.cos(angle - 2.5) * arrow_size * 0.6,
                     indicator_y + math.sin(angle - 2.5) * arrow_size * 0.6)
                ]
                
                if structure.type == "command":
                    color = RED
                elif structure.type == "nest":
                    color = GREEN
                else:
                    color = (150, 100, 50)
                
                pygame.draw.polygon(screen, color, arrow_points)
                
                distance = math.sqrt((structure.x - self.game.player.x)**2 + 
                                    (structure.y - self.game.player.y)**2)
                font = pygame.font.Font(None, 20)
                dist_text = font.render(f"{int(distance)}m", True, WHITE)
                screen.blit(dist_text, (indicator_x - 15, indicator_y + 20))