import pygame
import sys
import math
import random
from settings import *
from player import Helldiver
from enemies import Bug, Turret
from bullets import Bullet, Weapon
from stratagems import StratagemSystem, execute_stratagem
from effects import BloodEffect, ExplosionEffect, AirstrikeEffect
from ui import UI
from wave_manager import WaveManager
from screen_shake import ScreenShake
from sound_system import SoundSystem
from particles import ParticleSystem, DamageNumber, Particle
from destruction_mode import DestructionMode
from camera import Camera

class Game:
    def __init__(self, game_mode="destruction"):
        pygame.init()
        pygame.display.set_caption("HELLDIVERS: DEMOCRACY PROTOCOL")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.victory = False
        self.game_mode = game_mode
        
        self.screen_shake = ScreenShake()
        self.sound_system = SoundSystem()
        self.particle_system = ParticleSystem()
        
        self.player = Helldiver(SCREEN_WIDTH * 1.5, SCREEN_HEIGHT * 1.5)
        self.player.set_systems(self.particle_system, self.sound_system)
        
        self.stratagem_system = StratagemSystem()
        self.wave_manager = WaveManager()
        self.wave_manager.mode = game_mode
        self.ui = UI()
        
        self.bullets = []
        self.enemies = []
        self.effects = []
        self.turrets = []
        self.damage_numbers = []
        self.score = 0
        self.game_time = 0
        self.hit_stop_timer = 0
        
        self.blood_stains = []
        
        self.stratagem_key_held = False
        
        self.destruction_mode = None
        if game_mode == "destruction":
            self.destruction_mode = DestructionMode(self)
            # Set player map bounds
            self.player.set_map_bounds(self.destruction_mode.map_width, 
                                       self.destruction_mode.map_height)
            # Set wave manager map bounds
            self.wave_manager.map_width = self.destruction_mode.map_width
            self.wave_manager.map_height = self.destruction_mode.map_height
        else:
            self.player.set_map_bounds(SCREEN_WIDTH, SCREEN_HEIGHT)
            self.wave_manager.map_width = SCREEN_WIDTH
            self.wave_manager.map_height = SCREEN_HEIGHT
        
        self.start_new_wave()
    
    def start_new_wave(self):
        new_enemies = self.wave_manager.start_next_wave()
        self.enemies.extend(new_enemies)
        self.screen_shake.add_shake(5, 0.3)
    
    def add_damage_number(self, x, y, damage, color=WHITE):
        self.damage_numbers.append(DamageNumber(x, y, damage, color))
    
    def explode_grenade(self, grenade):
        """Handle grenade explosion with satisfying effects."""
        # Enhanced explosion particles
        self.particle_system.add_particles(
            self.particle_system.spawn_explosion(grenade.x, grenade.y, 120, 1.5)
        )
        
        # Add extra spark particles
        for _ in range(50):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(100, 600)
            self.particle_system.add_particles([
                Particle(
                    grenade.x, grenade.y,
                    math.cos(angle) * speed,
                    math.sin(angle) * speed,
                    random.uniform(0.2, 0.8),
                    random.choice([ORANGE, YELLOW, RED, WHITE, (255, 200, 50)]),
                    random.uniform(2, 6),
                    gravity=50
                )
            ])
        
        # Add explosion effect
        self.effects.append(ExplosionEffect(grenade.x, grenade.y, 0, 120))
        
        # Big screen shake
        self.screen_shake.add_shake(25, 0.8)
        
        # Sound
        self.sound_system.play('explosion')
        
        # Damage enemies (bigger radius, falloff damage)
        for enemy in self.enemies[:]:
            if enemy.alive:
                dist = math.sqrt((grenade.x - enemy.x)**2 + (grenade.y - enemy.y)**2)
                if dist < 200:
                    damage = grenade.damage * (1 - dist / 200) * 1.5
                    enemy.take_damage(damage)
                    self.add_damage_number(enemy.x, enemy.y - 20, int(damage), ORANGE)
                    
                    if not enemy.alive:
                        self.score += enemy.score_value
                        self.player.kills += 1
                        self.particle_system.add_particles(
                            self.particle_system.spawn_blood(enemy.x, enemy.y, 20)
                        )
                        self.sound_system.play('enemy_death')
                        self.blood_stains.append((enemy.x, enemy.y, enemy.radius))
                        if enemy in self.enemies:
                            self.enemies.remove(enemy)
        
        # Damage structures
        if self.destruction_mode:
            for structure in self.destruction_mode.structures[:]:
                if structure.alive and not structure.exploding:
                    dist = math.sqrt((grenade.x - structure.x)**2 + (grenade.y - structure.y)**2)
                    if dist < 200:
                        damage = grenade.damage * (1 - dist / 200) * 2
                        structure.take_damage(damage)
                        self.add_damage_number(structure.x, structure.y - 30, int(damage), RED)
            
            # Damage barrels in radius
            for barrel in self.destruction_mode.barrels[:]:
                if barrel.alive:
                    dist = math.sqrt((grenade.x - barrel.x)**2 + (grenade.y - barrel.y)**2)
                    if dist < 180:
                        self.destruction_mode.explode_barrel(barrel)
        
        # Damage player if too close (friendly fire)
        if self.player.alive:
            dist = math.sqrt((grenade.x - self.player.x)**2 + (grenade.y - self.player.y)**2)
            if dist < 150:
                damage = max(5, 60 - dist * 0.4)
                self.player.take_damage(damage, "self")
                self.add_damage_number(self.player.x, self.player.y - 30, int(damage), RED)
                self.screen_shake.add_shake(15, 0.3)
    
    def handle_events(self):
        keys = pygame.key.get_pressed()
        mouse_buttons = pygame.mouse.get_pressed()
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q and not self.stratagem_key_held:
                    self.stratagem_key_held = True
                    self.stratagem_system.start_input()
                    self.sound_system.play('stratagem_input')
                
                elif self.stratagem_system.input_active:
                    if event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                        result = self.stratagem_system.process_key(event.key)
                        if result and result != "failed":
                            self.execute_stratagem(result)
                            self.sound_system.play('stratagem_confirm')
                        elif result == "failed":
                            self.effects.append(ExplosionEffect(
                                self.player.x, self.player.y, 0.1, 20))
                            self.player.take_damage(10, "self")
                            self.screen_shake.add_shake(8, 0.3)
                            self.sound_system.play('stratagem_fail')
                            self.particle_system.add_particles(
                                self.particle_system.spawn_explosion(
                                    self.player.x, self.player.y, 30
                                )
                            )
                
                elif event.key == pygame.K_r:
                    if self.game_over or self.victory:
                        self.restart_game()
                    else:
                        self.player.weapon.start_reload(self.game_time)
                        self.sound_system.play('reload')
                
                elif event.key == pygame.K_SPACE:
                    self.player.dive()
                
                elif event.key == pygame.K_g:
                    grenade = self.player.throw_grenade()
                    if grenade:
                        self.bullets.append(grenade)
                
                elif event.key == pygame.K_1:
                    self.player.weapon = Weapon('rifle')
                elif event.key == pygame.K_2:
                    self.player.weapon = Weapon('shotgun')
                elif event.key == pygame.K_3:
                    self.player.weapon = Weapon('laser')
                elif event.key == pygame.K_4:
                    self.player.weapon = Weapon('smg')
                
                elif event.key == pygame.K_m:
                    if self.destruction_mode:
                        self.destruction_mode.minimap.toggle()
            
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_q:
                    self.stratagem_key_held = False
        
        if not self.game_over and not self.victory:
            dx = (keys[pygame.K_d] - keys[pygame.K_a])
            dy = (keys[pygame.K_s] - keys[pygame.K_w])
            sprinting = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
            
            self.player.move(dx, dy, sprinting, 1/60)
            
            # Convert mouse to world coordinates
            if self.destruction_mode:
                world_mouse_x = mouse_x + self.destruction_mode.camera.x
                world_mouse_y = mouse_y + self.destruction_mode.camera.y
                self.player.aim(world_mouse_x, world_mouse_y)
            else:
                self.player.aim(mouse_x, mouse_y)
            
            if mouse_buttons[0]:
                new_bullets = self.player.shoot(self.game_time)
                if new_bullets:
                    self.bullets.extend(new_bullets)
    
    def execute_stratagem(self, stratagem_name):
        if self.player.get_stratagem_cooldown(stratagem_name) > 0:
            return
        
        cooldown = STRATAGEM_COOLDOWNS.get(stratagem_name, 10)
        self.player.set_stratagem_cooldown(stratagem_name, cooldown)
        
        result = execute_stratagem(stratagem_name, self.player, 
                                  self.enemies, self.bullets, 
                                  self.effects, self.game_time)
        
        if result and isinstance(result, Turret):
            self.turrets.append(result)
    
    def update(self):
        if self.game_over or self.victory:
            return
        
        dt = 1/60
        
        if self.hit_stop_timer > 0:
            self.hit_stop_timer -= dt
            return
        
        self.game_time += dt
        
        self.screen_shake.update(dt)
        
        self.player.weapon.update(self.game_time)
        
        self.stratagem_system.update(dt)
        
        if self.wave_manager.should_start_wave():
            self.start_new_wave()
        
        self.wave_manager.update(dt, self.enemies)
        
        if self.destruction_mode:
            self.destruction_mode.update(dt)
        
        # Update bullets and handle collisions
        bullets_to_remove = []
        grenades_to_explode = []
        
        for bullet in self.bullets[:]:
            bullet.update(dt)
            
            # Check if grenade hits an enemy
            if bullet.is_grenade and not bullet.has_exploded:
                if bullet.check_enemy_collision(self.enemies):
                    # Grenade hit enemy - explode immediately
                    grenades_to_explode.append(bullet)
                    bullets_to_remove.append(bullet)
                    continue
            
            # Check if grenade timer expired
            if bullet.is_grenade and bullet.lifetime <= 0 and not bullet.has_exploded:
                bullet.has_exploded = True
                grenades_to_explode.append(bullet)
                bullets_to_remove.append(bullet)
                continue
            
            # Enemy bullets hitting player
            if bullet.owner == "enemy" and self.player.alive:
                if self.check_collision(bullet.x, bullet.y, bullet.radius,
                                      self.player.x, self.player.y, PLAYER_RADIUS):
                    self.player.take_damage(bullet.damage)
                    bullets_to_remove.append(bullet)
                    self.screen_shake.add_shake(3, 0.2)
                    self.particle_system.add_particles(
                        self.particle_system.spawn_bullet_impact(
                            bullet.x, bullet.y, bullet.angle
                        )
                    )
                    continue
            
            # Player bullets hitting enemies (skip grenades - they're handled above)
            if bullet.owner == "player" and not bullet.is_grenade:
                hit_enemy = False
                
                # Check structure hits
                if self.destruction_mode:
                    if self.destruction_mode.check_structure_hits(bullet):
                        bullets_to_remove.append(bullet)
                        hit_enemy = True
                        continue
                
                # Check enemy hits
                if not hit_enemy:
                    for enemy in self.enemies[:]:
                        if enemy.alive and self.check_collision(bullet.x, bullet.y, bullet.radius,
                                                               enemy.x, enemy.y, enemy.radius):
                            enemy.take_damage(bullet.damage)
                            bullets_to_remove.append(bullet)
                            hit_enemy = True
                            
                            self.sound_system.play('hit_enemy')
                            self.add_damage_number(enemy.x, enemy.y - 20, bullet.damage)
                            self.particle_system.add_particles(
                                self.particle_system.spawn_blood(enemy.x, enemy.y, 5)
                            )
                            
                            if not enemy.alive:
                                self.score += enemy.score_value
                                self.player.kills += 1
                                self.particle_system.add_particles(
                                    self.particle_system.spawn_blood(enemy.x, enemy.y, 20)
                                )
                                self.sound_system.play('enemy_death')
                                self.screen_shake.add_shake(5, 0.15)
                                self.hit_stop_timer = 0.05
                                self.blood_stains.append((enemy.x, enemy.y, enemy.radius))
                                
                                if enemy in self.enemies:
                                    self.enemies.remove(enemy)
                            break
                
                # Check turret hits
                if not hit_enemy:
                    for turret in self.turrets[:]:
                        if turret.alive and self.check_collision(bullet.x, bullet.y, bullet.radius,
                                                                turret.x, turret.y, turret.radius):
                            turret.take_damage(bullet.damage)
                            bullets_to_remove.append(bullet)
                            self.add_damage_number(turret.x, turret.y - 20, bullet.damage, ORANGE)
                            
                            if not turret.alive:
                                if turret in self.turrets:
                                    self.turrets.remove(turret)
                            break
            
            # Remove bullets that have expired (non-grenades)
            if bullet.lifetime <= 0 and not bullet.is_grenade:
                bullets_to_remove.append(bullet)
        
        # Remove bullets
        for bullet in bullets_to_remove:
            if bullet in self.bullets:
                self.bullets.remove(bullet)
        
        # Explode grenades
        for grenade in grenades_to_explode:
            self.explode_grenade(grenade)
        
        # Turret update
        for turret in self.turrets[:]:
            if turret.alive:
                new_bullet = turret.update(self.enemies, dt, self.game_time)
                if new_bullet:
                    self.bullets.append(new_bullet)
            else:
                if turret in self.turrets:
                    self.turrets.remove(turret)
        
        # Enemy update
        for enemy in self.enemies[:]:
            if enemy.alive:
                enemy.update(self.player.x, self.player.y, dt, self.game_time)
                
                # Spewer shooting with range check
                if enemy.type == "spewer" and enemy.shoot_timer <= 0:
                    dist = math.sqrt((enemy.x - self.player.x)**2 + (enemy.y - self.player.y)**2)
                    if dist < 500:
                        new_bullet = enemy.shoot_at_player(self.player.x, self.player.y, self.game_time)
                        if new_bullet:
                            self.bullets.append(new_bullet)
                
                # Enemy collision with player
                if self.player.alive and self.check_collision(
                    enemy.x, enemy.y, enemy.radius,
                    self.player.x, self.player.y, PLAYER_RADIUS):
                    self.player.take_damage(enemy.damage)
                    enemy.take_damage(50)
                    self.screen_shake.add_shake(5, 0.2)
                    
                    if not enemy.alive:
                        self.score += enemy.score_value
                        self.player.kills += 1
                        self.particle_system.add_particles(
                            self.particle_system.spawn_blood(enemy.x, enemy.y, 20)
                        )
                        self.sound_system.play('enemy_death')
                        self.blood_stains.append((enemy.x, enemy.y, enemy.radius))
                        if enemy in self.enemies:
                            self.enemies.remove(enemy)
        
        # Effects update
        for effect in self.effects[:]:
            effect.update(dt)
            
            if isinstance(effect, AirstrikeEffect) and effect.delay <= 0:
                if not effect.laser:
                    for bomb in effect.bombs:
                        if not bomb['exploded'] and bomb['timer'] <= 0:
                            bomb['exploded'] = True
                            self.damage_enemies_in_radius(bomb['x'], bomb['y'], 80, 100)
                            self.effects.append(ExplosionEffect(bomb['x'], bomb['y'], 0, 80))
                            
                            self.screen_shake.add_shake(15, 0.4)
                            self.sound_system.play('explosion')
                            self.particle_system.add_particles(
                                self.particle_system.spawn_explosion(bomb['x'], bomb['y'], 80)
                            )
                            
                            if self.destruction_mode:
                                for structure in self.destruction_mode.structures:
                                    if structure.alive and not structure.exploding:
                                        if self.check_collision(
                                            bomb['x'], bomb['y'], 0,
                                            structure.x, structure.y, 80):
                                            structure.take_damage(150)
                            
                            if self.player.alive and self.check_collision(
                                bomb['x'], bomb['y'], 0,
                                self.player.x, self.player.y, 80):
                                self.player.take_damage(50, "self")
                else:
                    if effect.laser_timer < 2.0:
                        self.damage_enemies_in_radius(effect.x, effect.y, 40, 10)
                        if self.player.alive and self.check_collision(
                            effect.x, effect.y, 0,
                            self.player.x, self.player.y, 40):
                            self.player.take_damage(5, "self")
            
            if effect.done:
                if effect in self.effects:
                    self.effects.remove(effect)
        
        self.particle_system.update(dt)
        
        for damage_num in self.damage_numbers[:]:
            damage_num.update(dt)
            if damage_num.lifetime <= 0:
                self.damage_numbers.remove(damage_num)
        
        if not self.player.alive:
            self.game_over = True
            self.screen_shake.add_shake(20, 1.0)
    
    def damage_enemies_in_radius(self, x, y, radius, damage):
        for enemy in self.enemies[:]:
            if enemy.alive and self.check_collision(x, y, 0, enemy.x, enemy.y, radius):
                enemy.take_damage(damage)
                self.add_damage_number(enemy.x, enemy.y - 20, damage, ORANGE)
                
                if not enemy.alive:
                    self.score += enemy.score_value
                    self.player.kills += 1
                    self.particle_system.add_particles(
                        self.particle_system.spawn_blood(enemy.x, enemy.y, 20)
                    )
                    self.sound_system.play('enemy_death')
                    self.blood_stains.append((enemy.x, enemy.y, enemy.radius))
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)
    
    def check_collision(self, x1, y1, r1, x2, y2, r2):
        distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
        return distance < (r1 + r2)
    
    def draw(self):
        shake_x, shake_y = self.screen_shake.get_offset()
        
        self.screen.fill(DARK_GREEN)
        
        if self.destruction_mode:
            camera_offset = self.destruction_mode.camera.get_offset()
            camera_offset = (camera_offset[0] + shake_x, camera_offset[1] + shake_y)
        else:
            camera_offset = (shake_x, shake_y)
        
        if self.destruction_mode:
            grid_size = 100
            start_x = int(self.destruction_mode.camera.x // grid_size) * grid_size
            start_y = int(self.destruction_mode.camera.y // grid_size) * grid_size
            
            for x in range(start_x, start_x + SCREEN_WIDTH + grid_size, grid_size):
                screen_x = x + camera_offset[0]
                pygame.draw.line(self.screen, (40, 70, 40), 
                               (screen_x, 0), (screen_x, SCREEN_HEIGHT), 1)
            
            for y in range(start_y, start_y + SCREEN_HEIGHT + grid_size, grid_size):
                screen_y = y + camera_offset[1]
                pygame.draw.line(self.screen, (40, 70, 40), 
                               (0, screen_y), (SCREEN_WIDTH, screen_y), 1)
        else:
            for x in range(0, SCREEN_WIDTH, 100):
                pygame.draw.line(self.screen, (40, 70, 40), 
                               (x + shake_x, 0), (x + shake_x, SCREEN_HEIGHT), 1)
            for y in range(0, SCREEN_HEIGHT, 100):
                pygame.draw.line(self.screen, (40, 70, 40), 
                               (0, y + shake_y), (SCREEN_WIDTH, y + shake_y), 1)
        
        # Draw blood stains
        for stain_x, stain_y, stain_radius in self.blood_stains:
            if self.destruction_mode:
                if not self.destruction_mode.camera.is_visible(stain_x, stain_y):
                    continue
            pygame.draw.circle(self.screen, (60, 0, 0), 
                             (int(stain_x + camera_offset[0]), 
                              int(stain_y + camera_offset[1])), 
                             stain_radius)
        
        if self.destruction_mode:
            self.destruction_mode.draw(self.screen)
        
        for effect in self.effects:
            effect.draw(self.screen)
        
        for turret in self.turrets:
            if self.destruction_mode:
                if not self.destruction_mode.camera.is_visible(turret.x, turret.y):
                    continue
                screen_x = turret.x + camera_offset[0]
                screen_y = turret.y + camera_offset[1]
                pygame.draw.circle(self.screen, (100, 100, 100), 
                                 (int(screen_x), int(screen_y)), turret.radius)
                pygame.draw.circle(self.screen, DARK_GRAY, 
                                 (int(screen_x), int(screen_y)), 10)
            else:
                turret.draw(self.screen)
        
        for enemy in self.enemies:
            if self.destruction_mode:
                if not self.destruction_mode.camera.is_visible(enemy.x, enemy.y):
                    continue
                screen_x = enemy.x + camera_offset[0]
                screen_y = enemy.y + camera_offset[1]
                pygame.draw.circle(self.screen, enemy.color, 
                                 (int(screen_x), int(screen_y)), enemy.radius)
                
                eye_offset = enemy.radius * 0.4
                pygame.draw.circle(self.screen, (255, 0, 0), 
                                 (int(screen_x - eye_offset), int(screen_y - eye_offset)), 3)
                pygame.draw.circle(self.screen, (255, 0, 0), 
                                 (int(screen_x + eye_offset), int(screen_y - eye_offset)), 3)
            else:
                enemy.draw(self.screen)
        
        # Draw bullets with camera offset
        for bullet in self.bullets:
            bullet.draw(self.screen, camera_offset)
        
        if self.player.alive:
            if self.destruction_mode:
                screen_x = self.player.x + camera_offset[0]
                screen_y = self.player.y + camera_offset[1]
                
                pygame.draw.circle(self.screen, self.player.body_color, 
                                 (int(screen_x), int(screen_y)), PLAYER_RADIUS)
                
                gun_length = 20
                gun_x = screen_x + math.cos(self.player.angle) * gun_length
                gun_y = screen_y + math.sin(self.player.angle) * gun_length
                pygame.draw.line(self.screen, DARK_GRAY, 
                               (screen_x, screen_y), (gun_x, gun_y), 4)
                
                visor_x = screen_x + math.cos(self.player.angle) * 6
                visor_y = screen_y + math.sin(self.player.angle) * 6
                pygame.draw.circle(self.screen, WHITE, 
                                 (int(visor_x), int(visor_y)), 3)
            else:
                self.player.draw(self.screen, camera_offset)
        
        self.particle_system.draw(self.screen, camera_offset)
        
        for damage_num in self.damage_numbers:
            damage_num.draw(self.screen, camera_offset)
        
        if not self.game_over and not self.victory:
            self.ui.draw_hud(self.screen, self.player, self.score, 
                           self.wave_manager.current_wave, self.game_time,
                           self.stratagem_system)
            
            if self.destruction_mode:
                self.destruction_mode.draw_ui(self.screen)
                self.destruction_mode.draw_off_screen_indicators(self.screen)
            
            self.stratagem_system.draw(self.screen)
        elif self.victory:
            self.draw_victory_screen()
        else:
            self.ui.draw_game_over(self.screen, self.score, 
                                  self.wave_manager.current_wave)
        
        pygame.display.flip()
    
    def draw_victory_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        font_large = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 36)
        
        victory_text = font_large.render("MISSION COMPLETE!", True, GREEN)
        text_rect = victory_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
        self.screen.blit(victory_text, text_rect)
        
        score_text = font_medium.render(f"SCORE: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        self.screen.blit(score_text, score_rect)
        
        if self.destruction_mode:
            struct_text = font_medium.render(
                f"STRUCTURES DESTROYED: {self.destruction_mode.structures_destroyed}/{self.destruction_mode.total_structures}",
                True, WHITE
            )
            struct_rect = struct_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            self.screen.blit(struct_text, struct_rect)
        
        restart_text = font_medium.render("PRESS R TO PLAY AGAIN", True, YELLOW)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 150))
        self.screen.blit(restart_text, restart_rect)
    
    def restart_game(self):
        self.blood_stains = []
        self.__init__(game_mode=self.game_mode)
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game(game_mode="destruction")
    game.run()