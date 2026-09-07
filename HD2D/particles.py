import pygame
import random
import math
from settings import *

class Particle:
    def __init__(self, x, y, vx, vy, lifetime, color, size=3, gravity=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.color = color
        self.size = size
        self.gravity = gravity
        
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += self.gravity * dt
        self.lifetime -= dt
        
    def draw(self, screen, camera_offset=(0, 0)):
        alpha = self.lifetime / self.max_lifetime
        color = (int(self.color[0] * alpha), 
                int(self.color[1] * alpha), 
                int(self.color[2] * alpha))
        
        draw_x = self.x + camera_offset[0]
        draw_y = self.y + camera_offset[1]
        pygame.draw.circle(screen, color, (int(draw_x), int(draw_y)), self.size)

class ParticleSystem:
    def __init__(self):
        self.particles = []
        
    def add_particles(self, particles):
        self.particles.extend(particles)
        
    def spawn_bullet_impact(self, x, y, angle):
        """Spawn particles when bullet hits something."""
        particles = []
        for _ in range(5):
            spread_angle = angle + random.uniform(-0.5, 0.5)
            speed = random.uniform(50, 150)
            particles.append(Particle(
                x, y,
                math.cos(spread_angle) * speed,
                math.sin(spread_angle) * speed,
                random.uniform(0.2, 0.5),
                YELLOW,
                random.uniform(2, 4)
            ))
        return particles
    
    def spawn_muzzle_flash(self, x, y, angle):
        """Spawn muzzle flash particles."""
        particles = []
        for _ in range(3):
            spread_angle = angle + random.uniform(-0.3, 0.3)
            speed = random.uniform(100, 200)
            particles.append(Particle(
                x, y,
                math.cos(spread_angle) * speed,
                math.sin(spread_angle) * speed,
                random.uniform(0.05, 0.15),
                (255, 200, 50),
                random.uniform(3, 5)
            ))
        return particles
    
    def spawn_shell_casing(self, x, y, angle):
        """Spawn shell casing particle."""
        eject_angle = angle + math.pi / 2
        speed = random.uniform(50, 100)
        
        return [Particle(
            x, y,
            math.cos(eject_angle) * speed,
            math.sin(eject_angle) * speed,
            random.uniform(0.5, 1.0),
            (200, 150, 50),
            2,
            gravity=300
        )]
    
    def spawn_blood(self, x, y, amount=15):
        """Spawn blood particles."""
        particles = []
        for _ in range(amount):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 200)
            particles.append(Particle(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                random.uniform(0.5, 1.5),
                BLOOD_RED,
                random.uniform(2, 5)
            ))
        return particles
    
    def spawn_explosion(self, x, y, radius=50, intensity=1.0):
        """Spawn enhanced explosion particles with intensity multiplier."""
        particles = []
        
        # Main explosion - fiery particles
        num_particles = int(40 * intensity)
        for _ in range(num_particles):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(100, 500 * intensity)
            color = random.choice([
                ORANGE, YELLOW, RED, 
                (255, 200, 50),   # Bright yellow
                (255, 150, 0),    # Deep orange
                (255, 255, 200),  # Almost white hot
                (200, 100, 0)     # Dark orange
            ])
            particles.append(Particle(
                x + random.uniform(-15, 15),
                y + random.uniform(-15, 15),
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                random.uniform(0.3, 1.2 * intensity),
                color,
                random.uniform(3, 10 * intensity),
                gravity=50
            ))
        
        # Smoke particles
        for _ in range(int(20 * intensity)):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(30, 150 * intensity)
            gray = 80 + random.randint(0, 80)
            particles.append(Particle(
                x + random.uniform(-30, 30),
                y + random.uniform(-30, 30),
                math.cos(angle) * speed,
                math.sin(angle) * speed - 50,
                random.uniform(1.0, 3.0 * intensity),
                (gray, gray, gray),
                random.uniform(8, 20 * intensity),
                gravity=-20  # Smoke rises
            ))
        
        # Spark particles (flying debris)
        for _ in range(int(30 * intensity)):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(200, 700 * intensity)
            color = random.choice([
                WHITE, YELLOW, (255, 200, 150),
                (255, 220, 100), (200, 200, 255)
            ])
            particles.append(Particle(
                x + random.uniform(-8, 8),
                y + random.uniform(-8, 8),
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                random.uniform(0.1, 0.5 * intensity),
                color,
                random.uniform(2, 5 * intensity),
                gravity=100
            ))
        
        # Ring particles (expanding shockwave effect)
        for i in range(12):
            angle = (i / 12) * math.pi * 2
            particles.append(Particle(
                x + math.cos(angle) * radius * 0.5,
                y + math.sin(angle) * radius * 0.5,
                math.cos(angle) * 300 * intensity,
                math.sin(angle) * 300 * intensity,
                random.uniform(0.2, 0.5 * intensity),
                (255, 200, 100, 100),
                random.uniform(4, 8 * intensity)
            ))
        
        # Fireball core (bright center)
        for _ in range(10):
            particles.append(Particle(
                x + random.uniform(-20, 20),
                y + random.uniform(-20, 20),
                random.uniform(-50, 50),
                random.uniform(-50, 50),
                random.uniform(0.1, 0.3 * intensity),
                (255, 255, 255),
                random.uniform(8, 15 * intensity)
            ))
        
        return particles
    
    def spawn_footstep(self, x, y):
        """Spawn dust particles for footsteps."""
        return [Particle(
            x + random.uniform(-5, 5),
            y + random.uniform(-5, 5),
            random.uniform(-20, 20),
            random.uniform(-20, 20),
            random.uniform(0.3, 0.5),
            (150, 140, 120),
            random.uniform(2, 4)
        )]
    
    def spawn_grenade_trail(self, x, y):
        """Spawn trail sparks for grenade."""
        particles = []
        for _ in range(3):
            particles.append(Particle(
                x + random.uniform(-3, 3),
                y + random.uniform(-3, 3),
                random.uniform(-20, 20),
                random.uniform(-20, 20),
                random.uniform(0.1, 0.3),
                ORANGE,
                random.uniform(1, 3)
            ))
        return particles
    
    def update(self, dt):
        for particle in self.particles[:]:
            particle.update(dt)
            if particle.lifetime <= 0:
                self.particles.remove(particle)
    
    def draw(self, screen, camera_offset=(0, 0)):
        for particle in self.particles:
            particle.draw(screen, camera_offset)

class DamageNumber:
    def __init__(self, x, y, damage, color=WHITE):
        self.x = x
        self.y = y
        self.damage = damage
        self.color = color
        self.lifetime = 1.0
        self.max_lifetime = 1.0
        self.vy = -100
        self.font = pygame.font.Font(None, 24)
        
    def update(self, dt):
        self.y += self.vy * dt
        self.vy *= 0.95
        self.lifetime -= dt
        
    def draw(self, screen, camera_offset=(0, 0)):
        alpha = self.lifetime / self.max_lifetime
        text = self.font.render(str(self.damage), True, self.color)
        text.set_alpha(int(255 * alpha))
        draw_x = self.x + camera_offset[0] - text.get_width() // 2
        draw_y = self.y + camera_offset[1] - text.get_height() // 2
        screen.blit(text, (draw_x, draw_y))