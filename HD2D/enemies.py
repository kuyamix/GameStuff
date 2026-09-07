import pygame
import math
import random
from settings import *
from bullets import Bullet

class Bug:
    def __init__(self, x, y, bug_type="scavenger"):
        self.x = x
        self.y = y
        self.type = bug_type
        self.settings = ENEMY_SETTINGS[bug_type]
        
        self.health = self.settings['health']
        self.max_health = self.settings['health']
        self.speed = self.settings['speed']
        self.damage = self.settings['damage']
        self.radius = self.settings['radius']
        self.color = self.settings['color']
        self.score_value = self.settings['score']
        
        self.alive = True
        self.flash_timer = 0
        
        # Special behaviors
        if bug_type == "charger":
            self.charging = False
            self.charge_timer = random.uniform(1.0, 2.0)
            self.charge_angle = 0
        elif bug_type == "spewer":
            self.shoot_timer = random.uniform(2.0, 4.0)
        elif bug_type == "stalker":
            self.invisible = True
            self.reveal_timer = 0
            self.stealth_timer = random.uniform(2.0, 4.0)
        
        # Animation
        self.animation_timer = 0
        self.leg_offset = random.uniform(0, math.pi * 2)
        
    def update(self, player_x, player_y, dt, current_time):
        if not self.alive:
            return
            
        self.flash_timer = max(0, self.flash_timer - dt)
        self.animation_timer += dt
        
        angle = math.atan2(player_y - self.y, player_x - self.x)
        
        # Special behaviors
        if self.type == "charger":
            self.charge_timer -= dt
            if self.charge_timer <= 0:
                self.charging = not self.charging
                self.charge_timer = random.uniform(1.0, 2.0)
                if self.charging:
                    self.charge_angle = angle
            
            if self.charging:
                speed = self.speed * 3
                move_angle = self.charge_angle
            else:
                speed = self.speed
                move_angle = angle
        elif self.type == "stalker":
            self.stealth_timer -= dt
            if self.stealth_timer <= 0:
                self.invisible = not self.invisible
                if self.invisible:
                    self.stealth_timer = random.uniform(2.0, 4.0)
                    self.reveal_timer = 0
                else:
                    self.stealth_timer = random.uniform(0.5, 1.0)
            
            speed = self.speed
            move_angle = angle
        elif self.type == "spewer":
            # Decrement shoot timer for spewers
            self.shoot_timer -= dt
            speed = self.speed
            move_angle = angle
        else:
            speed = self.speed
            move_angle = angle
        
        # Move towards player - NO SCREEN CLAMPING
        self.x += math.cos(move_angle) * speed * dt
        self.y += math.sin(move_angle) * speed * dt
    
    def take_damage(self, damage):
        self.health -= damage
        self.flash_timer = 0.1
        if self.health <= 0:
            self.alive = False
    
    def shoot_at_player(self, player_x, player_y, current_time):
        """For ranged enemies like spewers"""
        if not self.alive:
            return None
            
        self.shoot_timer = random.uniform(2.0, 4.0)
        angle = math.atan2(player_y - self.y, player_x - self.x)
        return Bullet(self.x, self.y, angle, 200, self.damage, "enemy")
    
    def draw(self, screen):
        if not self.alive:
            return
            
        # Handle invisibility for stalkers
        if self.type == "stalker" and self.invisible:
            # Draw semi-transparent
            alpha_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(alpha_surface, (*self.color, 50), 
                             (self.radius, self.radius), self.radius)
            screen.blit(alpha_surface, (self.x - self.radius, self.y - self.radius))
            return
        
        # Draw body
        color = RED if self.flash_timer > 0 else self.color
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        
        # Draw armor/pattern details
        if self.type == "warrior":
            pygame.draw.circle(screen, (100, 80, 30), 
                             (int(self.x), int(self.y)), self.radius - 3, 2)
        elif self.type == "charger":
            pygame.draw.circle(screen, (100, 50, 25), 
                             (int(self.x), int(self.y)), self.radius - 5, 3)
        
        # Draw eyes
        eye_offset = self.radius * 0.4
        eye_size = max(2, self.radius * 0.25)
        pygame.draw.circle(screen, (255, 0, 0), 
                          (int(self.x - eye_offset), int(self.y - eye_offset)), eye_size)
        pygame.draw.circle(screen, (255, 0, 0), 
                          (int(self.x + eye_offset), int(self.y - eye_offset)), eye_size)
        
        # Draw legs (animated)
        leg_animation = math.sin(self.animation_timer * 10 + self.leg_offset) * 3
        for i in range(6):
            leg_angle = (i / 6) * math.pi * 2
            leg_x1 = self.x + math.cos(leg_angle) * self.radius
            leg_y1 = self.y + math.sin(leg_angle) * self.radius
            leg_x2 = self.x + math.cos(leg_angle) * (self.radius + 4 + leg_animation)
            leg_y2 = self.y + math.sin(leg_angle) * (self.radius + 4 + leg_animation)
            pygame.draw.line(screen, (80, 60, 40), 
                           (leg_x1, leg_y1), (leg_x2, leg_y2), 2)
        
        # Health bar for damaged enemies
        if self.health < self.max_health:
            bar_width = self.radius * 2
            bar_height = 3
            bar_x = self.x - bar_width // 2
            bar_y = self.y - self.radius - 8
            health_percent = self.health / self.max_health
            pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(screen, GREEN, 
                           (bar_x, bar_y, bar_width * health_percent, bar_height))

class Turret:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = 200
        self.alive = True
        self.angle = 0
        self.shoot_timer = 0
        self.radius = 15
        self.damage = 15
        self.color = (100, 100, 100)
        self.target = None
        
    def update(self, enemies, dt, current_time):
        if not self.alive:
            return
            
        # Find closest enemy
        closest_enemy = None
        closest_distance = float('inf')
        for enemy in enemies:
            if enemy.alive:
                dist = math.sqrt((enemy.x - self.x)**2 + (enemy.y - self.y)**2)
                if dist < closest_distance and dist < 400:
                    closest_enemy = enemy
                    closest_distance = dist
        
        self.target = closest_enemy
        
        # Shoot at target
        if self.target:
            self.angle = math.atan2(self.target.y - self.y, self.target.x - self.x)
            self.shoot_timer -= dt
            if self.shoot_timer <= 0:
                self.shoot_timer = 0.2
                return Bullet(self.x, self.y, self.angle, 600, self.damage, "player")
        return None
    
    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False
    
    def draw(self, screen):
        if not self.alive:
            return
            
        # Draw base
        pygame.draw.rect(screen, DARK_GRAY, 
                        (self.x - 15, self.y - 15, 30, 30))
        
        # Draw rotating turret
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 10)
        gun_x = self.x + math.cos(self.angle) * 20
        gun_y = self.y + math.sin(self.angle) * 20
        pygame.draw.line(screen, BLACK, (self.x, self.y), (gun_x, gun_y), 4)