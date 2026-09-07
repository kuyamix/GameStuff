import math
from config import *

# ============ GAME STATE ============
class GameState:
    def __init__(self):
        self.player_x = MAP_WIDTH // 2
        self.player_y = MAP_HEIGHT // 2
        self.player_health = 100
        self.player_max_health = 100
        self.player_speed = 4.0
        self.player_size = 22
        self.level = 1
        self.xp = 0
        self.xp_to_next = 30
        self.game_time = 0
        self.enemies_killed = 0
        self.level_up_notifications = []
        self.camera_x = self.player_x
        self.camera_y = self.player_y
        self.zoom_level = 1.0
        self.aiming_mode = False
        self.aiming_ability = None
        self.aim_x = 0
        self.aim_y = 0
        self.enemies = []
        self.gems = []
        self.enemy_spawn_timer = 0
        self.keys = {'up': False, 'down': False, 'left': False, 'right': False}
        
        # Cooldowns
        self.strafe_cooldown = 0
        self.mortar_cooldown = 0
        self.mrls_cooldown = 0
        
        # Ability states
        self.strafe_active = False
        self.mortar_phase = 0
        self.mrls_active = False
        self.mrls_phase = 0
        
        # Ability data (initialized empty)
        self.strafe_x = self.strafe_y = self.strafe_angle = 0
        self.strafe_particles = []
        self.strafe_bullets = []
        self.mortar_shells = []
        self.mortar_impact_effects = []
        self.mrls_rockets = []
        self.mrls_explosions = []
        self.mortar_flash = self.mrls_flash = 0
        self.mrls_warning_timer = 0
        # In GameState.__init__() add:
        self.mrls_total_rockets = 12  # Increased from 5 for more spread coverage
# ============ HELPERS ============
def world_to_screen(wx, wy, cx, cy, zoom):
    return (wx - cx) * zoom + SCREEN_WIDTH//2, (wy - cy) * zoom + SCREEN_HEIGHT//2

def screen_to_world(sx, sy, cx, cy, zoom):
    return (sx - SCREEN_WIDTH//2) / zoom + cx, (sy - SCREEN_HEIGHT//2) / zoom + cy

def distance(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)

def clamp(v, mn, mx):
    return max(mn, min(v, mx))

def is_unlocked(level, ability):
    return level >= UNLOCK_LEVELS.get(ability, 999)