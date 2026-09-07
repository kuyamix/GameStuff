import pygame
import math
import random
import numpy as np

class SoundSystem:
    def __init__(self):
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        self.sounds = {}
        self.enabled = True
        self.volume = 0.5
        self.generate_all_sounds()
        
    def generate_all_sounds(self):
        """Generate all game sounds procedurally."""
        self.sounds['shoot_rifle'] = self.generate_gunshot(800, 0.1, 0.3)
        self.sounds['shoot_shotgun'] = self.generate_gunshot(400, 0.2, 0.5)
        self.sounds['shoot_laser'] = self.generate_laser_sound()
        self.sounds['shoot_smg'] = self.generate_gunshot(900, 0.05, 0.2)
        self.sounds['explosion'] = self.generate_explosion()
        self.sounds['hit_enemy'] = self.generate_hit_sound()
        self.sounds['enemy_death'] = self.generate_enemy_death()
        self.sounds['player_hurt'] = self.generate_player_hurt()
        self.sounds['stratagem_input'] = self.generate_beep(1000)
        self.sounds['stratagem_confirm'] = self.generate_beep(1500)
        self.sounds['stratagem_fail'] = self.generate_beep(200)
        self.sounds['reload'] = self.generate_reload_sound()
        self.sounds['dive'] = self.generate_dive_sound()
        self.sounds['grenade_throw'] = self.generate_throw_sound()
        
    def generate_gunshot(self, frequency, duration, noise_amount):
        """Generate a gunshot sound."""
        sample_rate = 22050
        num_samples = int(duration * sample_rate)
        
        # Create sound buffer
        buffer = np.zeros((num_samples, 2), dtype=np.int16)
        
        for i in range(num_samples):
            t = i / sample_rate
            
            # Main frequency with decay
            envelope = math.exp(-t * 30)  # Fast decay
            main_wave = math.sin(2 * math.pi * frequency * t) * envelope
            
            # Add noise
            noise = random.uniform(-1, 1) * noise_amount * envelope
            
            # Mix
            sample = (main_wave * 0.7 + noise * 0.3) * 32767 * 0.3
            
            # Apply to both channels with slight variation
            buffer[i][0] = int(sample)
            buffer[i][1] = int(sample * random.uniform(0.8, 1.0))
        
        sound = pygame.sndarray.make_sound(buffer)
        sound.set_volume(self.volume * 0.5)
        return sound
    
    def generate_laser_sound(self):
        """Generate laser pew sound."""
        sample_rate = 22050
        duration = 0.15
        num_samples = int(duration * sample_rate)
        
        buffer = np.zeros((num_samples, 2), dtype=np.int16)
        
        for i in range(num_samples):
            t = i / sample_rate
            
            # Frequency sweep
            frequency = 1200 - 800 * t  # Descending pitch
            
            envelope = math.exp(-t * 20)
            wave = math.sin(2 * math.pi * frequency * t) * envelope
            
            sample = wave * 32767 * 0.4
            buffer[i][0] = int(sample)
            buffer[i][1] = int(sample)
        
        sound = pygame.sndarray.make_sound(buffer)
        sound.set_volume(self.volume * 0.4)
        return sound
    
    def generate_explosion(self):
        """Generate explosion sound."""
        sample_rate = 22050
        duration = 1.0
        num_samples = int(duration * sample_rate)
        
        buffer = np.zeros((num_samples, 2), dtype=np.int16)
        
        for i in range(num_samples):
            t = i / sample_rate
            
            # Low frequency rumble
            rumble = math.sin(2 * math.pi * 60 * t) * math.exp(-t * 4)
            
            # Noise component
            noise = random.uniform(-1, 1) * math.exp(-t * 6)
            
            # Mix
            sample = (rumble * 0.5 + noise * 0.5) * 32767 * 0.7
            
            buffer[i][0] = int(sample)
            buffer[i][1] = int(sample * random.uniform(0.9, 1.0))
        
        sound = pygame.sndarray.make_sound(buffer)
        sound.set_volume(self.volume * 0.8)
        return sound
    
    def generate_hit_sound(self):
        """Generate hit marker sound."""
        sample_rate = 22050
        duration = 0.1
        num_samples = int(duration * sample_rate)
        
        buffer = np.zeros((num_samples, 2), dtype=np.int16)
        
        for i in range(num_samples):
            t = i / sample_rate
            
            frequency = 800
            envelope = math.exp(-t * 40)
            wave = math.sin(2 * math.pi * frequency * t) * envelope
            
            sample = wave * 32767 * 0.3
            buffer[i][0] = int(sample)
            buffer[i][1] = int(sample)
        
        sound = pygame.sndarray.make_sound(buffer)
        sound.set_volume(self.volume * 0.3)
        return sound
    
    def generate_enemy_death(self):
        """Generate enemy death squish sound."""
        sample_rate = 22050
        duration = 0.3
        num_samples = int(duration * sample_rate)
        
        buffer = np.zeros((num_samples, 2), dtype=np.int16)
        
        for i in range(num_samples):
            t = i / sample_rate
            
            frequency = 400 - 300 * t  # Descending
            envelope = math.exp(-t * 10)
            wave = math.sin(2 * math.pi * frequency * t) * envelope
            
            # Add some noise for squish
            noise = random.uniform(-1, 1) * math.exp(-t * 8) * 0.3
            
            sample = (wave + noise) * 32767 * 0.4
            buffer[i][0] = int(sample)
            buffer[i][1] = int(sample)
        
        sound = pygame.sndarray.make_sound(buffer)
        sound.set_volume(self.volume * 0.5)
        return sound
    
    def generate_player_hurt(self):
        """Generate player hurt sound."""
        sample_rate = 22050
        duration = 0.2
        num_samples = int(duration * sample_rate)
        
        buffer = np.zeros((num_samples, 2), dtype=np.int16)
        
        for i in range(num_samples):
            t = i / sample_rate
            
            frequency = 200 - 100 * t
            envelope = math.exp(-t * 15)
            wave = math.sin(2 * math.pi * frequency * t) * envelope
            
            sample = wave * 32767 * 0.5
            buffer[i][0] = int(sample)
            buffer[i][1] = int(sample)
        
        sound = pygame.sndarray.make_sound(buffer)
        sound.set_volume(self.volume * 0.6)
        return sound
    
    def generate_beep(self, frequency):
        """Generate simple beep for stratagem input."""
        sample_rate = 22050
        duration = 0.1
        num_samples = int(duration * sample_rate)
        
        buffer = np.zeros((num_samples, 2), dtype=np.int16)
        
        for i in range(num_samples):
            t = i / sample_rate
            
            envelope = math.exp(-t * 30)
            wave = math.sin(2 * math.pi * frequency * t) * envelope
            
            sample = wave * 32767 * 0.5
            buffer[i][0] = int(sample)
            buffer[i][1] = int(sample)
        
        sound = pygame.sndarray.make_sound(buffer)
        sound.set_volume(self.volume * 0.7)
        return sound
    
    def generate_reload_sound(self):
        """Generate reload click sound."""
        sample_rate = 22050
        duration = 0.4
        num_samples = int(duration * sample_rate)
        
        buffer = np.zeros((num_samples, 2), dtype=np.int16)
        
        # First click
        for i in range(num_samples // 2):
            t = i / sample_rate
            frequency = 1500
            envelope = math.exp(-t * 50)
            wave = math.sin(2 * math.pi * frequency * t) * envelope
            sample = wave * 32767 * 0.4
            buffer[i][0] = int(sample)
            buffer[i][1] = int(sample)
        
        # Second click
        for i in range(num_samples // 2, num_samples):
            t = (i - num_samples // 2) / sample_rate
            frequency = 1200
            envelope = math.exp(-t * 50)
            wave = math.sin(2 * math.pi * frequency * t) * envelope
            sample = wave * 32767 * 0.4
            buffer[i][0] = int(sample)
            buffer[i][1] = int(sample)
        
        sound = pygame.sndarray.make_sound(buffer)
        sound.set_volume(self.volume * 0.5)
        return sound
    
    def generate_dive_sound(self):
        """Generate dive whoosh sound."""
        sample_rate = 22050
        duration = 0.3
        num_samples = int(duration * sample_rate)
        
        buffer = np.zeros((num_samples, 2), dtype=np.int16)
        
        for i in range(num_samples):
            t = i / sample_rate
            
            # Whoosh - filtered noise
            noise = random.uniform(-1, 1)
            envelope = math.sin(math.pi * t / duration)  # Fade in/out
            filter_freq = 500 + 1000 * t
            
            sample = noise * envelope * math.sin(2 * math.pi * filter_freq * t) * 32767 * 0.3
            buffer[i][0] = int(sample)
            buffer[i][1] = int(sample)
        
        sound = pygame.sndarray.make_sound(buffer)
        sound.set_volume(self.volume * 0.3)
        return sound
    
    def generate_throw_sound(self):
        """Generate grenade throw sound."""
        sample_rate = 22050
        duration = 0.2
        num_samples = int(duration * sample_rate)
        
        buffer = np.zeros((num_samples, 2), dtype=np.int16)
        
        for i in range(num_samples):
            t = i / sample_rate
            
            frequency = 600 - 200 * t
            envelope = math.exp(-t * 20)
            wave = math.sin(2 * math.pi * frequency * t) * envelope
            
            sample = wave * 32767 * 0.3
            buffer[i][0] = int(sample)
            buffer[i][1] = int(sample)
        
        sound = pygame.sndarray.make_sound(buffer)
        sound.set_volume(self.volume * 0.4)
        return sound
    
    def play(self, sound_name):
        """Play a sound by name."""
        if self.enabled and sound_name in self.sounds:
            self.sounds[sound_name].play()
    
    def toggle_sound(self):
        self.enabled = not self.enabled
        return self.enabled