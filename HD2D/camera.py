import pygame
import math
from settings import *

class Camera:
    def __init__(self, map_width, map_height, screen_width, screen_height):
        self.map_width = map_width
        self.map_height = map_height
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = 0
        self.y = 0
        
    def update(self, target_x, target_y, dt):
        """Smoothly follow target."""
        target_camera_x = target_x - self.screen_width // 2
        target_camera_y = target_y - self.screen_height // 2
        
        lerp_speed = 5.0 * dt
        self.x += (target_camera_x - self.x) * lerp_speed
        self.y += (target_camera_y - self.y) * lerp_speed
        
        # Clamp to map bounds
        self.x = max(0, min(self.x, self.map_width - self.screen_width))
        self.y = max(0, min(self.y, self.map_height - self.screen_height))
    
    def apply(self, world_x, world_y):
        """Convert world coordinates to screen coordinates."""
        screen_x = world_x - self.x
        screen_y = world_y - self.y
        return (screen_x, screen_y)
    
    def get_offset(self):
        """Get the offset to apply to world positions for screen drawing."""
        return (-self.x, -self.y)
    
    def is_visible(self, world_x, world_y, margin=100):
        """Check if world position is visible on screen."""
        screen_x, screen_y = self.apply(world_x, world_y)
        return (-margin <= screen_x <= self.screen_width + margin and
                -margin <= screen_y <= self.screen_height + margin)
    
    def get_visible_bounds(self, margin=50):
        """Get visible world bounds."""
        return {
            'left': self.x - margin,
            'right': self.x + self.screen_width + margin,
            'top': self.y - margin,
            'bottom': self.y + self.screen_height + margin
        }