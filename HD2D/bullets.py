import pygame
import math
import random
from settings import *

class Bullet:
    def __init__(self, x, y, angle, speed, damage, owner="player", explosive=False, is_grenade=False):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.damage = damage
        self.owner = owner
        self.explosive = explosive
        self.is_grenade = is_grenade
        self.lifetime = 2.0
        self.radius = 3
        self.explosion_radius = 50 if explosive else 0
        
        # Grenade specific
        if is_grenade:
            self.radius = 8
            self.lifetime = 2.0  # Explode after 2 seconds
            self.bounce_count = 0
            self.max_bounces = 2
            self.gravity = 0  # No gravity - straight line
            self.vy = 0  # No vertical velocity
            self.fuse_spark = 0
            self.has_exploded = False  # Track if grenade already exploded
        
        # Trail effect
        self.trail = []
        self.trail_timer = 0
        
        # Map bounds (set by game)
        self.map_width = SCREEN_WIDTH * 3
        self.map_height = SCREEN_HEIGHT * 3
        
    def set_map_bounds(self, map_width, map_height):
        """Set map bounds for grenade bouncing."""
        self.map_width = map_width
        self.map_height = map_height
        
    def update(self, dt):
        if self.is_grenade:
            # Grenade moves in straight line (no gravity arc)
            self.x += math.cos(self.angle) * self.speed * dt
            self.y += math.sin(self.angle) * self.speed * dt
            
            # Fuse spark animation
            self.fuse_spark += dt
            
            # Bounce off walls
            if self.bounce_count < self.max_bounces:
                if self.x < self.radius:
                    self.x = self.radius
                    self.angle = math.pi - self.angle
                    self.bounce_count += 1
                    self.speed *= 0.8
                elif self.x > self.map_width - self.radius:
                    self.x = self.map_width - self.radius
                    self.angle = math.pi - self.angle
                    self.bounce_count += 1
                    self.speed *= 0.8
                
                if self.y < self.radius:
                    self.y = self.radius
                    self.angle = -self.angle
                    self.bounce_count += 1
                    self.speed *= 0.8
                elif self.y > self.map_height - self.radius:
                    self.y = self.map_height - self.radius
                    self.angle = -self.angle
                    self.bounce_count += 1
                    self.speed *= 0.8
        else:
            self.x += math.cos(self.angle) * self.speed * dt
            self.y += math.sin(self.angle) * self.speed * dt
            
        self.lifetime -= dt
        
        # Update trail
        self.trail_timer += dt
        if self.trail_timer > 0.02:
            self.trail.append((self.x, self.y))
            self.trail_timer = 0
            if len(self.trail) > 15:
                self.trail.pop(0)
    
    def check_enemy_collision(self, enemies):
        """Check if grenade hits any enemy."""
        if not self.is_grenade or self.has_exploded:
            return False
        
        for enemy in enemies:
            if enemy.alive:
                dist = math.sqrt((self.x - enemy.x)**2 + (self.y - enemy.y)**2)
                if dist < (self.radius + enemy.radius):
                    self.has_exploded = True
                    self.lifetime = 0  # Trigger explosion
                    return True
        return False
    
    def draw(self, screen, camera_offset=(0, 0)):
        """Draw bullet with camera offset applied."""
        draw_x = self.x + camera_offset[0]
        draw_y = self.y + camera_offset[1]
        
        # Draw trail with offset
        for i, (tx, ty) in enumerate(self.trail):
            alpha = i / len(self.trail)
            if self.is_grenade:
                color = (int(200 * alpha), int(100 * alpha), int(50 * alpha))
            else:
                color = (int(255 * alpha), int(255 * alpha), int(100 * alpha))
            size = 3 if self.is_grenade else 2
            trail_draw_x = tx + camera_offset[0]
            trail_draw_y = ty + camera_offset[1]
            pygame.draw.circle(screen, color, (int(trail_draw_x), int(trail_draw_y)), size)
        
        # Draw bullet/grenade
        if self.is_grenade:
            # Check if about to explode (fuse burning faster)
            fuse_intensity = 1.0
            if self.lifetime < 0.5:
                fuse_intensity = 1.0 + (0.5 - self.lifetime) * 2
            
            # Grenade body
            pygame.draw.circle(screen, (100, 100, 100), (int(draw_x), int(draw_y)), self.radius)
            pygame.draw.circle(screen, (60, 60, 60), (int(draw_x), int(draw_y)), self.radius, 2)
            
            # Grenade pattern (ridges)
            for i in range(4):
                angle_ridge = (i / 4) * math.pi * 2 + self.fuse_spark * 2
                ridge_x = draw_x + math.cos(angle_ridge) * (self.radius * 0.7)
                ridge_y = draw_y + math.sin(angle_ridge) * (self.radius * 0.7)
                pygame.draw.circle(screen, (80, 80, 80), (int(ridge_x), int(ridge_y)), 2)
            
            # Fuse spark (pulsing - faster when about to explode)
            spark_size = 4 + math.sin(self.fuse_spark * 8 * fuse_intensity) * (1.5 * fuse_intensity)
            spark_x = draw_x + math.cos(self.angle) * self.radius
            spark_y = draw_y + math.sin(self.angle) * self.radius - 4
            
            # Spark color changes when about to explode
            if self.lifetime < 0.5:
                spark_color = RED
            else:
                spark_color = ORANGE
            
            pygame.draw.circle(screen, spark_color, (int(spark_x), int(spark_y)), int(spark_size))
            pygame.draw.circle(screen, YELLOW, (int(spark_x), int(spark_y)), int(spark_size * 0.5))
            
            # Fuse line
            fuse_end_x = draw_x + math.cos(self.angle) * (self.radius + 6)
            fuse_end_y = draw_y + math.sin(self.angle) * (self.radius + 6) - 4
            pygame.draw.line(screen, (150, 100, 50), 
                           (spark_x, spark_y), 
                           (fuse_end_x, fuse_end_y), 2)
            
            # Glow effect (brighter when about to explode)
            glow_intensity = 1.0 if self.lifetime >= 0.5 else 2.0
            glow_size = (self.radius + 5 + math.sin(self.fuse_spark * 4) * 2) * glow_intensity
            glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            alpha = 30 if self.lifetime >= 0.5 else 60
            pygame.draw.circle(glow_surface, (255, 150, 50, alpha), 
                             (glow_size, glow_size), glow_size)
            screen.blit(glow_surface, (draw_x - glow_size, draw_y - glow_size))
            
            # Draw timer text above grenade
            if self.lifetime < 1.0:
                font = pygame.font.Font(None, 16)
                timer_text = font.render(f"{self.lifetime:.1f}", True, RED)
                screen.blit(timer_text, (draw_x - 10, draw_y - self.radius - 20))
            
        elif self.owner == "player":
            color = YELLOW
            pygame.draw.circle(screen, color, (int(draw_x), int(draw_y)), self.radius)
            # Glow for player bullets
            glow_surface = pygame.Surface((self.radius * 4, self.radius * 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (255, 255, 100, 30), 
                             (self.radius * 2, self.radius * 2), self.radius * 2)
            screen.blit(glow_surface, (draw_x - self.radius * 2, draw_y - self.radius * 2))
        else:
            color = RED
            pygame.draw.circle(screen, color, (int(draw_x), int(draw_y)), self.radius)
        
        # Draw glow for explosive bullets (not grenades)
        if self.explosive and not self.is_grenade:
            pygame.draw.circle(screen, ORANGE, (int(draw_x), int(draw_y)), self.radius + 2, 1)

class Weapon:
    def __init__(self, weapon_type):
        self.type = weapon_type
        self.settings = WEAPON_SETTINGS[weapon_type]
        
        self.damage = self.settings['damage']
        self.fire_rate = self.settings['fire_rate']
        self.bullet_speed = self.settings['bullet_speed']
        self.spread = self.settings['spread']
        self.pellets = self.settings['pellets']
        self.color = self.settings['color']
        
        self.ammo = self.settings['ammo']
        self.max_ammo = self.settings['ammo']
        self.reload_time = self.settings['reload_time']
        self.reloading = False
        self.reload_start = 0
        self.last_shot = 0
        self.original_spread = self.spread
        
    def shoot(self, x, y, angle, current_time):
        if current_time - self.last_shot < self.fire_rate:
            return []
        if self.reloading:
            return []
        if self.ammo <= 0:
            self.start_reload(current_time)
            return []
            
        self.last_shot = current_time
        self.ammo -= 1
        
        bullets = []
        for _ in range(self.pellets):
            spread_angle = angle + random.uniform(-self.spread, self.spread)
            bullets.append(Bullet(x, y, spread_angle, 
                                 self.bullet_speed, self.damage, "player"))
        
        # Auto reload when empty
        if self.ammo <= 0 and self.type != 'laser':
            self.start_reload(current_time)
            
        return bullets
    
    def start_reload(self, current_time):
        if not self.reloading and self.ammo < self.max_ammo and self.type != 'laser':
            self.reloading = True
            self.reload_start = current_time
    
    def update(self, current_time):
        if self.reloading and current_time - self.reload_start >= self.reload_time:
            self.reloading = False
            self.ammo = self.max_ammo
    
    def reset_spread(self):
        self.spread = self.original_spread