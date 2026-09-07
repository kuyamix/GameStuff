import pygame
import math
from settings import *
from effects import ExplosionEffect, AirstrikeEffect

class StratagemSystem:
    def __init__(self):
        self.input_buffer = []
        self.input_active = False
        self.input_timer = 0
        self.max_input_time = 1.5
        self.current_stratagem = None
        
    def start_input(self):
        self.input_active = True
        self.input_buffer = []
        self.input_timer = 0
        self.current_stratagem = None
    
    def cancel_input(self):
        self.input_active = False
        self.input_buffer = []
        self.current_stratagem = None
    
    def process_key(self, key):
        if not self.input_active:
            return None
            
        self.input_buffer.append(key)
        
        # Check if buffer matches any stratagem
        for name, code in STRATAGEM_CODES.items():
            if self.input_buffer == code[:len(self.input_buffer)]:
                # Partial match, continue
                if len(self.input_buffer) == len(code):
                    # Complete match
                    self.cancel_input()
                    return name
                return None  # Still matching
        
        # No match found, cancel
        self.cancel_input()
        return "failed"
    
    def update(self, dt):
        if self.input_active:
            self.input_timer += dt
            if self.input_timer > self.max_input_time:
                self.cancel_input()
    
    def draw(self, screen):
        if not self.input_active:
            return
            
        # Draw input prompt
        font = pygame.font.Font(None, 36)
        text = font.render("INPUT STRATAGEM:", True, WHITE)
        screen.blit(text, (50, SCREEN_HEIGHT - 100))
        
        # Draw arrows
        arrow_positions = [150, 190, 230, 270, 310]
        arrows = [pygame.K_UP, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT, pygame.K_UP]
        arrow_symbols = ["↑", "→", "↓", "←", "↑"]
        
        for i, pos in enumerate(arrow_positions):
            if i < len(self.input_buffer):
                color = GREEN
            else:
                color = DARK_GRAY
            
            # Draw arrow box
            pygame.draw.rect(screen, color, (pos, SCREEN_HEIGHT - 105, 25, 25))
            text = font.render(arrow_symbols[i], True, BLACK)
            screen.blit(text, (pos + 5, SCREEN_HEIGHT - 105))

def execute_stratagem(name, player, enemies, bullets, effects, current_time):
    """Execute a stratagem and return any created objects"""
    if name == "airstrike":
        # Airstrike targets area in front of player
        target_x = player.x + math.cos(player.angle) * 300
        target_y = player.y + math.sin(player.angle) * 300
        effects.append(AirstrikeEffect(target_x, target_y, 0.5))
        return None
        
    elif name == "supply":
        # Supply drop heals and restores ammo
        effects.append(ExplosionEffect(player.x, player.y - 50, 0.5, 30))
        player.heal(50)
        if player.weapon.type != 'laser':
            player.weapon.ammo = player.weapon.max_ammo
        player.grenades = min(3, player.grenades + 1)
        return None
        
    elif name == "turret":
        # Deploy turret near player
        from enemies import Turret
        turret_x = player.x + math.cos(player.angle) * 50
        turret_y = player.y + math.sin(player.angle) * 50
        return Turret(turret_x, turret_y)
        
    elif name == "orbital_laser":
        # Orbital laser targets player position
        effects.append(AirstrikeEffect(player.x, player.y, 1.0, laser=True))
        return None
        
    elif name == "reinforce":
        # Revive all dead players
        if not player.alive:
            player.alive = True
            player.health = player.max_health
            player.x = SCREEN_WIDTH // 2
            player.y = SCREEN_HEIGHT // 2
        effects.append(ExplosionEffect(player.x, player.y - 50, 0.3, 20))
        return None
    
    return None