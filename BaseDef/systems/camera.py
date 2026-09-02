from constants import SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT

class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.zoom = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 2.0
        self.world_width = WORLD_WIDTH
        self.world_height = WORLD_HEIGHT
    
    def apply_zoom(self, zoom_change):
        self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom + zoom_change))
    
    def world_to_screen(self, world_x, world_y):
        screen_x = (world_x - self.x) * self.zoom
        screen_y = (world_y - self.y) * self.zoom
        return int(screen_x), int(screen_y)
    
    def screen_to_world(self, screen_x, screen_y):
        world_x = screen_x / self.zoom + self.x
        world_y = screen_y / self.zoom + self.y
        return int(world_x), int(world_y)
    
    def center_on(self, world_x, world_y):
        self.x = world_x - (SCREEN_WIDTH / 2) / self.zoom
        self.y = world_y - (SCREEN_HEIGHT / 2) / self.zoom
        self._clamp()
    
    def move(self, dx, dy):
        self.x += dx / self.zoom
        self.y += dy / self.zoom
        self._clamp()
    
    def _clamp(self):
        self.x = max(0, min(self.x, self.world_width - SCREEN_WIDTH / self.zoom))
        self.y = max(0, min(self.y, self.world_height - SCREEN_HEIGHT / self.zoom))