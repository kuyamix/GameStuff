import random
import math
from settings import *
from enemies import Bug

class WaveManager:
    def __init__(self):
        self.current_wave = 0
        self.enemies_remaining = 0
        self.wave_active = False
        self.wave_timer = 0
        self.between_waves = True
        self.mode = "survival"  # "survival" or "destruction"
        
        # Map bounds (set by game)
        self.map_width = SCREEN_WIDTH * 3
        self.map_height = SCREEN_HEIGHT * 3
        
    def start_next_wave(self):
        self.current_wave += 1
        self.wave_active = True
        self.between_waves = False
        self.wave_timer = 0
        
        # Calculate number of enemies based on mode
        if self.mode == "destruction":
            # Fewer enemies in destruction mode (structures spawn their own)
            num_enemies = 3 + (self.current_wave - 1) * 2
        else:
            num_enemies = BASE_ENEMIES_PER_WAVE + (self.current_wave - 1) * ENEMIES_PER_WAVE_INCREMENT
        
        self.enemies_remaining = num_enemies
        
        # Spawn enemies
        new_enemies = []
        for _ in range(num_enemies):
            enemy = self.spawn_enemy()
            new_enemies.append(enemy)
        
        return new_enemies
    
    def spawn_enemy(self):
        # Spawn from random edge of the MAP
        side = random.choice(['top', 'bottom', 'left', 'right'])
        
        margin = 50
        if side == 'top':
            x = random.randint(margin, self.map_width - margin)
            y = -30
        elif side == 'bottom':
            x = random.randint(margin, self.map_width - margin)
            y = self.map_height + 30
        elif side == 'left':
            x = -30
            y = random.randint(margin, self.map_height - margin)
        else:  # right
            x = self.map_width + 30
            y = random.randint(margin, self.map_height - margin)
        
        # Choose enemy type based on wave and mode
        enemy_type = self.choose_enemy_type()
        return Bug(x, y, enemy_type)
    
    def choose_enemy_type(self):
        # Wave-based enemy composition
        if self.current_wave <= 2:
            return 'scavenger'
        elif self.current_wave <= 4:
            return random.choice(['scavenger', 'scavenger', 'warrior'])
        elif self.current_wave <= 6:
            return random.choice(['scavenger', 'warrior', 'warrior', 'spewer'])
        elif self.current_wave <= 8:
            return random.choice(['warrior', 'warrior', 'spewer', 'charger'])
        elif self.current_wave <= 10:
            return random.choice(['warrior', 'spewer', 'charger', 'stalker'])
        else:
            return random.choice(['scavenger', 'warrior', 'charger', 'spewer', 'stalker'])
    
    def update(self, dt, enemies):
        if not self.wave_active:
            return
        
        # Check if wave is complete
        alive_enemies = [e for e in enemies if e.alive]
        if len(alive_enemies) == 0 and self.enemies_remaining <= 0:
            self.wave_active = False
            self.between_waves = True
            self.wave_timer = WAVE_INTERVAL
        
        # Spawn remaining enemies over time
        if self.enemies_remaining > 0:
            self.wave_timer -= dt
            if self.wave_timer <= 0:
                self.wave_timer = 1.0
                new_enemy = self.spawn_enemy()
                enemies.append(new_enemy)
                self.enemies_remaining -= 1
    
    def should_start_wave(self):
        return self.between_waves and not self.wave_active