import pygame
import math
import random
from settings import *

class Particle:
    def __init__(self, x, y, velocity_x, velocity_y, lifetime, color, size=3):
        self.x = x
        self.y = y
        self.vx = velocity_x
        self.vy = velocity_y
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.color = color
        self.size = size
        
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        self.vx *= 0.98
        self.vy *= 0.98
        
    def draw(self, screen):
        alpha = self.lifetime / self.max_lifetime
        color = (int(self.color[0] * alpha), 
                int(self.color[1] * alpha), 
                int(self.color[2] * alpha))
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)

class BloodEffect:
    def __init__(self, x, y, color=(139, 0, 0)):
        self.particles = []
        self.done = False
        self.color = color
        
        for _ in range(15):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 200)
            self.particles.append(Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                random.uniform(0.5, 1.5),
                color,
                random.uniform(2, 5)
            ))
    
    def update(self, dt):
        for particle in self.particles:
            particle.update(dt)
        self.particles = [p for p in self.particles if p.lifetime > 0]
        if len(self.particles) == 0:
            self.done = True
    
    def draw(self, screen):
        for particle in self.particles:
            particle.draw(screen)

class ExplosionEffect:
    def __init__(self, x, y, delay=0, radius=50):
        self.x = x
        self.y = y
        self.delay = delay
        self.radius = radius
        self.particles = []
        self.done = False
        self.flash = 1.0
        self.ring_radius = 0
        self.ring_expanding = True
        
        # Create explosion particles with more variety
        for _ in range(30):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(100, 400)
            color = random.choice([ORANGE, YELLOW, RED, (255, 200, 50), (255, 150, 0)])
            self.particles.append(Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                random.uniform(0.3, 1.0),
                color,
                random.uniform(3, 8)
            ))
        
        # Smoke particles
        for _ in range(10):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 150)
            gray = 100 + random.randint(0, 80)
            self.particles.append(Particle(
                x + random.uniform(-10, 10),
                y + random.uniform(-10, 10),
                math.cos(angle) * speed,
                math.sin(angle) * speed - 30,
                random.uniform(1.0, 2.0),
                (gray, gray, gray),
                random.uniform(5, 12)
            ))
    
    def update(self, dt):
        if self.delay > 0:
            self.delay -= dt
            return
            
        self.flash -= dt * 5
        self.ring_radius += dt * 400
        if self.ring_radius > self.radius * 2:
            self.ring_expanding = False
            
        for particle in self.particles:
            particle.update(dt)
        self.particles = [p for p in self.particles if p.lifetime > 0]
        if len(self.particles) == 0 and self.flash <= 0:
            self.done = True
    
    def draw(self, screen):
        if self.delay > 0:
            return
            
        # Draw flash
        if self.flash > 0:
            flash_radius = int(self.radius * self.flash)
            # Outer glow
            pygame.draw.circle(screen, (255, 200, 50, 50), 
                             (int(self.x), int(self.y)), flash_radius * 1.5)
            # Inner flash
            pygame.draw.circle(screen, WHITE, 
                             (int(self.x), int(self.y)), flash_radius)
        
        # Draw expanding ring
        if self.ring_expanding and self.ring_radius < self.radius * 2:
            alpha = 255 - (self.ring_radius / (self.radius * 2)) * 255
            ring_color = (200, 150, 50, int(alpha))
            # Use a surface for alpha ring since pygame doesn't support alpha in draw
            ring_surface = pygame.Surface((self.ring_radius * 2, self.ring_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(ring_surface, (200, 150, 50, int(alpha * 0.5)), 
                             (self.ring_radius, self.ring_radius), int(self.ring_radius), 3)
            screen.blit(ring_surface, (self.x - self.ring_radius, self.y - self.ring_radius))
        
        # Draw particles
        for particle in self.particles:
            particle.draw(screen)

class AirstrikeEffect:
    def __init__(self, x, y, delay=1.0, laser=False):
        self.x = x
        self.y = y
        self.delay = delay
        self.laser = laser
        self.done = False
        self.bombs = []
        self.laser_timer = 0
        
        if not laser:
            # Create bomb positions in a line with more spread
            for i in range(-4, 5):
                bomb_x = x + i * 50 + random.uniform(-10, 10)
                bomb_y = y + random.uniform(-20, 20)
                self.bombs.append({
                    'x': bomb_x,
                    'y': bomb_y,
                    'exploded': False,
                    'timer': delay + abs(i) * 0.08 + random.uniform(0, 0.05)
                })
    
    def update(self, dt):
        if self.delay > 0:
            self.delay -= dt
            return
        
        if self.laser:
            self.laser_timer += dt
            if self.laser_timer > 2.5:
                self.done = True
        else:
            all_exploded = True
            for bomb in self.bombs:
                if not bomb['exploded']:
                    bomb['timer'] -= dt
                    if bomb['timer'] <= 0:
                        bomb['exploded'] = True
                    all_exploded = False
            
            if all_exploded:
                self.done = True
    
    def draw(self, screen):
        if self.delay > 0:
            # Draw targeting reticle with animation
            pulse = math.sin(pygame.time.get_ticks() * 0.005) * 5
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 40 + pulse, 2)
            pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), 20 + pulse, 1)
            pygame.draw.line(screen, RED, (self.x - 50, self.y), (self.x + 50, self.y), 2)
            pygame.draw.line(screen, RED, (self.x, self.y - 50), (self.x, self.y + 50), 2)
            
            # Draw crosshair dots
            for i in range(4):
                angle = (i / 4) * math.pi * 2
                dot_x = self.x + math.cos(angle) * 30
                dot_y = self.y + math.sin(angle) * 30
                pygame.draw.circle(screen, RED, (int(dot_x), int(dot_y)), 3)
            
            # Draw "INCOMING" text
            font = pygame.font.Font(None, 24)
            text = font.render("INCOMING AIRSTRIKE!", True, RED)
            screen.blit(text, (self.x - text.get_width() // 2, self.y - 60))
            return
        
        if self.laser:
            # Draw orbital laser with glow
            laser_width = 8 + math.sin(self.laser_timer * 4) * 2
            
            # Outer glow
            for i in range(5):
                glow_width = laser_width + i * 4
                alpha = 50 - i * 8
                glow_surface = pygame.Surface((glow_width * 2, self.y + 50), pygame.SRCALPHA)
                pygame.draw.rect(glow_surface, (255, 50, 0, alpha), 
                               (0, 0, glow_width * 2, self.y + 50))
                screen.blit(glow_surface, (self.x - glow_width, 0))
            
            # Main laser
            pygame.draw.rect(screen, (255, 200, 50), 
                           (self.x - laser_width // 2, 0, laser_width, int(self.y)))
            pygame.draw.rect(screen, WHITE, 
                           (self.x - laser_width // 4, 0, laser_width // 2, int(self.y)))
            
            # Laser particles
            for i in range(20):
                particle_y = random.randint(0, int(self.y))
                particle_x = self.x + random.randint(-8, 8)
                pygame.draw.circle(screen, ORANGE, 
                                 (int(particle_x), particle_y), random.randint(2, 5))
        else:
            # Draw explosions for bombs that haven't exploded yet
            for bomb in self.bombs:
                if not bomb['exploded']:
                    # Draw bomb marker
                    pulse = math.sin(pygame.time.get_ticks() * 0.01 + bomb['x']) * 3
                    pygame.draw.circle(screen, RED, (int(bomb['x']), int(bomb['y'])), 8 + pulse)
                    pygame.draw.line(screen, RED, 
                                   (bomb['x'] - 15, bomb['y']), 
                                   (bomb['x'] + 15, bomb['y']), 2)
                    pygame.draw.line(screen, RED, 
                                   (bomb['x'], bomb['y'] - 15), 
                                   (bomb['x'], bomb['y'] + 15), 2)