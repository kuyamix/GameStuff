import pygame
import math
import random
from settings import *
from bullets import Bullet, Weapon
from particles import ParticleSystem

class Helldiver:
    def __init__(self, x, y, weapon_type='rifle', is_player_1=True):
        self.x = x
        self.y = y
        self.angle = 0
        self.health = PLAYER_MAX_HEALTH
        self.max_health = PLAYER_MAX_HEALTH
        self.stamina = PLAYER_MAX_STAMINA
        self.alive = True
        self.is_player_1 = is_player_1
        
        # Movement
        self.speed = PLAYER_SPEED
        self.diving = False
        self.dive_timer = 0
        self.dive_angle = 0
        self.footstep_timer = 0
        
        # Limb system
        self.leg_injured = False
        self.arm_injured = False
        
        # Weapon
        self.weapon = Weapon(weapon_type)
        self.grenades = 8
        self.grenade_cooldown = 0
        
        # Stratagems
        self.stratagem_cooldowns = {}
        for stratagem in STRATAGEM_COOLDOWNS:
            self.stratagem_cooldowns[stratagem] = 0
        
        # Visual
        self.body_color = BLUE if is_player_1 else GREEN
        self.visor_color = WHITE
        self.flash_timer = 0
        self.muzzle_flash = 0
        self.recoil_offset = 0
        
        # Particle system reference (set by game)
        self.particle_system = None
        
        # Sound system reference (set by game)
        self.sound_system = None
        
        # Stats
        self.kills = 0
        self.friendly_fire_hits = 0
        
        # Map bounds (will be set by game)
        self.map_width = SCREEN_WIDTH * 3
        self.map_height = SCREEN_HEIGHT * 3
        
    def set_systems(self, particle_system, sound_system):
        self.particle_system = particle_system
        self.sound_system = sound_system
    
    def set_map_bounds(self, map_width, map_height):
        """Set the map bounds for the player."""
        self.map_width = map_width
        self.map_height = map_height
        
    def move(self, dx, dy, sprinting, dt):
        if not self.alive:
            return
            
        # Handle dive
        if self.diving:
            self.dive_timer -= dt
            if self.dive_timer <= 0:
                self.diving = False
            else:
                self.x += math.cos(self.dive_angle) * PLAYER_DIVE_SPEED * dt
                self.y += math.sin(self.dive_angle) * PLAYER_DIVE_SPEED * dt
                
                # Spawn dive particles
                if self.particle_system and random.random() < 0.5:
                    self.particle_system.add_particles(
                        self.particle_system.spawn_footstep(self.x, self.y)
                    )
        else:
            speed = self.speed
            if sprinting and self.stamina > 0:
                speed *= PLAYER_SPRINT_MULTIPLIER
                self.stamina -= 25 * dt
            elif sprinting and self.stamina <= 0:
                speed *= 0.8
                
            if self.leg_injured:
                speed *= 0.6
                
            # Normalize diagonal movement
            if dx != 0 and dy != 0:
                dx *= 0.707
                dy *= 0.707
                
            self.x += dx * speed * dt
            self.y += dy * speed * dt
            
            # Footstep particles
            if dx != 0 or dy != 0:
                self.footstep_timer -= dt
                if self.footstep_timer <= 0:
                    self.footstep_timer = 0.3 if not sprinting else 0.15
                    if self.particle_system:
                        self.particle_system.add_particles(
                            self.particle_system.spawn_footstep(self.x, self.y)
                        )
        
        # Clamp to map bounds (not screen bounds!)
        self.x = max(PLAYER_RADIUS, min(self.x, self.map_width - PLAYER_RADIUS))
        self.y = max(PLAYER_RADIUS, min(self.y, self.map_height - PLAYER_RADIUS))
        
        # Regenerate stamina
        if not sprinting:
            self.stamina = min(PLAYER_MAX_STAMINA, self.stamina + 20 * dt)
        
        # Update timers
        self.flash_timer = max(0, self.flash_timer - dt)
        self.muzzle_flash = max(0, self.muzzle_flash - dt)
        self.grenade_cooldown = max(0, self.grenade_cooldown - dt)
        self.recoil_offset *= 0.9
        
        for stratagem in self.stratagem_cooldowns:
            self.stratagem_cooldowns[stratagem] = max(0, self.stratagem_cooldowns[stratagem] - dt)
    
    def aim(self, mouse_x, mouse_y):
        if self.alive:
            self.angle = math.atan2(mouse_y - self.y, mouse_x - self.x)
    
    def dive(self):
        if not self.diving and self.alive:
            self.diving = True
            self.dive_timer = PLAYER_DIVE_DURATION
            self.dive_angle = self.angle
            self.stamina -= 20
            
            if self.sound_system:
                self.sound_system.play('dive')
            
            if self.particle_system:
                for _ in range(10):
                    self.particle_system.add_particles(
                        self.particle_system.spawn_footstep(self.x, self.y)
                    )
    
    def shoot(self, current_time):
        if not self.alive or self.diving:
            return []
        
        bullets = self.weapon.shoot(self.x, self.y, self.angle, current_time)
        if bullets:
            self.muzzle_flash = 0.1
            self.recoil_offset = 3
            
            if self.sound_system:
                sound_name = f'shoot_{self.weapon.type}'
                self.sound_system.play(sound_name)
            
            if self.particle_system:
                muzzle_x = self.x + math.cos(self.angle) * 25
                muzzle_y = self.y + math.sin(self.angle) * 25
                self.particle_system.add_particles(
                    self.particle_system.spawn_muzzle_flash(muzzle_x, muzzle_y, self.angle)
                )
                
                if self.weapon.type != 'laser':
                    self.particle_system.add_particles(
                        self.particle_system.spawn_shell_casing(self.x, self.y, self.angle)
                    )
        
        return bullets
    
    def throw_grenade(self):
        """Throw a grenade in a straight line."""
        if self.grenades > 0 and self.grenade_cooldown <= 0 and self.alive:
            self.grenades -= 1
            self.grenade_cooldown = 0.5
            
            if self.sound_system:
                self.sound_system.play('grenade_throw')
            
            # Create grenade with straight trajectory (no gravity)
            grenade = Bullet(
                self.x + math.cos(self.angle) * 20,  # Spawn slightly in front
                self.y + math.sin(self.angle) * 20,
                self.angle,
                400,  # Speed - fast enough to reach enemies
                80,   # Damage
                "player",
                explosive=True,
                is_grenade=True
            )
            # Set map bounds for bouncing
            grenade.set_map_bounds(self.map_width, self.map_height)
            return grenade
        return None
    
    def take_damage(self, damage, source="enemy"):
        if not self.alive:
            return
            
        self.health -= damage
        self.flash_timer = 0.2
        
        if self.sound_system:
            self.sound_system.play('player_hurt')
        
        if self.particle_system:
            self.particle_system.add_particles(
                self.particle_system.spawn_blood(self.x, self.y, 10)
            )
        
        if self.health <= 0:
            self.alive = False
            self.health = 0
        elif self.health < 40 and not self.leg_injured:
            self.leg_injured = True
        elif self.health < 25 and not self.arm_injured:
            self.arm_injured = True
            self.weapon.spread *= 1.5
    
    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
        if self.health > 40:
            self.leg_injured = False
        if self.health > 25:
            self.arm_injured = False
            self.weapon.reset_spread()
    
    def get_stratagem_cooldown(self, stratagem_name):
        return self.stratagem_cooldowns.get(stratagem_name, 0)
    
    def set_stratagem_cooldown(self, stratagem_name, cooldown):
        self.stratagem_cooldowns[stratagem_name] = cooldown
    
    def draw(self, screen, camera_offset=(0, 0)):
        if not self.alive:
            return
        
        draw_x = self.x + camera_offset[0]
        draw_y = self.y + camera_offset[1]
        
        # Apply recoil offset
        recoil_x = -math.cos(self.angle) * self.recoil_offset
        recoil_y = -math.sin(self.angle) * self.recoil_offset
        draw_x += recoil_x
        draw_y += recoil_y
        
        # Draw shadow
        pygame.draw.ellipse(screen, (0, 0, 0, 50), 
                           (draw_x - 15, draw_y + 8, 30, 8))
        
        # Draw cape (behind body)
        if not self.diving:
            cape_angle = self.angle + math.pi
            cape_wave = math.sin(pygame.time.get_ticks() * 0.005) * 3
            cape_points = [
                (draw_x + math.cos(cape_angle - 0.5) * 15, 
                 draw_y + math.sin(cape_angle - 0.5) * 15),
                (draw_x + math.cos(cape_angle + 0.5) * 15, 
                 draw_y + math.sin(cape_angle + 0.5) * 15),
                (draw_x + math.cos(cape_angle) * (25 + cape_wave), 
                 draw_y + math.sin(cape_angle) * (25 + cape_wave))
            ]
            pygame.draw.polygon(screen, (100, 100, 150), cape_points)
        
        # Draw body
        color = RED if self.flash_timer > 0 else self.body_color
        pygame.draw.circle(screen, color, (int(draw_x), int(draw_y)), PLAYER_RADIUS)
        
        # Draw armor details
        pygame.draw.circle(screen, DARK_GRAY, (int(draw_x), int(draw_y)), PLAYER_RADIUS, 2)
        
        # Draw gun
        gun_length = 20
        gun_x = draw_x + math.cos(self.angle) * gun_length
        gun_y = draw_y + math.sin(self.angle) * gun_length
        pygame.draw.line(screen, DARK_GRAY, (draw_x, draw_y), (gun_x, gun_y), 4)
        
        # Draw muzzle flash
        if self.muzzle_flash > 0:
            flash_x = draw_x + math.cos(self.angle) * 25
            flash_y = draw_y + math.sin(self.angle) * 25
            flash_size = random.randint(5, 10)
            pygame.draw.circle(screen, YELLOW, (int(flash_x), int(flash_y)), flash_size)
            pygame.draw.circle(screen, WHITE, (int(flash_x), int(flash_y)), flash_size // 2)
        
        # Draw helmet visor
        visor_x = draw_x + math.cos(self.angle) * 6
        visor_y = draw_y + math.sin(self.angle) * 6
        pygame.draw.circle(screen, self.visor_color, (int(visor_x), int(visor_y)), 3)
        
        # Draw health bar
        if self.health < self.max_health:
            bar_width = 30
            bar_height = 4
            bar_x = draw_x - bar_width // 2
            bar_y = draw_y - PLAYER_RADIUS - 10
            health_percent = self.health / self.max_health
            pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, GREEN, (bar_x, bar_y, bar_width * health_percent, bar_height))
        
        # Draw grenade indicator
        grenade_text = pygame.font.Font(None, 16).render(f"G:{self.grenades}", True, WHITE)
        screen.blit(grenade_text, (draw_x - 15, draw_y + PLAYER_RADIUS + 5))