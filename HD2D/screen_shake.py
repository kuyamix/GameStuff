import random
import math

class ScreenShake:
    def __init__(self):
        self.intensity = 0
        self.duration = 0
        self.max_intensity = 0
        self.decay_rate = 0.9  # How fast shake dies down
        
    def add_shake(self, intensity, duration):
        """Add screen shake. Intensity in pixels, duration in seconds."""
        self.intensity = max(self.intensity, intensity)
        self.max_intensity = self.intensity
        self.duration = max(self.duration, duration)
        
    def update(self, dt):
        if self.duration > 0:
            self.duration -= dt
            # Decay intensity over time
            self.intensity *= (1 - self.decay_rate * dt)
            if self.duration <= 0:
                self.intensity = 0
                self.max_intensity = 0
    
    def get_offset(self):
        """Get random offset for screen shake."""
        if self.intensity <= 0:
            return (0, 0)
        
        # Random offset within intensity radius
        angle = random.uniform(0, math.pi * 2)
        distance = random.uniform(0, self.intensity)
        offset_x = math.cos(angle) * distance
        offset_y = math.sin(angle) * distance
        
        return (offset_x, offset_y)
    
    def get_intensity_ratio(self):
        """Get current intensity as ratio of max (0.0 to 1.0)."""
        if self.max_intensity <= 0:
            return 0
        return self.intensity / self.max_intensity