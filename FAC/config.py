import pygame

# ============ INITIALIZE PYGAME FIRST ============
pygame.init()

# ============ SCREEN ============
info = pygame.display.Info()
SCREEN_WIDTH = max(800, min(940, int(info.current_w * 0.7)))
SCREEN_HEIGHT = max(600, min(2030, int(info.current_h * 0.85)))

# ============ MAP ============
MAP_WIDTH = 4500
MAP_HEIGHT = 4500

# ============ COLORS ============
BLACK = (10, 10, 20)
WHITE = (255, 255, 255)
RED = (200, 30, 30)
GREEN = (50, 200, 50)
BLUE = (30, 150, 255)
PURPLE = (180, 50, 255)
YELLOW = (255, 255, 50)
ORANGE = (255, 150, 30)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
CYAN = (0, 255, 255)
GOLD = (255, 215, 0)
CRIMSON = (220, 20, 60)
MAROON = (128, 0, 0)
STEEL = (70, 130, 180)
SLATE = (112, 128, 144)
DARK_RED = (139, 0, 0)
DARK_PURPLE = (75, 0, 130)

# ============ LEVEL SYSTEM ============
UNLOCK_LEVELS = {'strafe': 1, 'mortar': 3, 'mrls': 6}
BASE_STATS = {'health_bonus': 5, 'speed_bonus': 0.1, 'cooldown_reduction': 0.02}

# ============ ENEMY TYPES ============
ENEMY_TYPES = {
    'grunt': {'hp': 25, 'speed': 1.5, 'size': 18, 'color': RED, 'xp': 10, 'damage': 8},
    'tank': {'hp': 100, 'speed': 0.7, 'size': 30, 'color': PURPLE, 'xp': 30, 'damage': 18},
    'fast': {'hp': 15, 'speed': 3.2, 'size': 14, 'color': (255, 100, 100), 'xp': 12, 'damage': 6},
    'heavy': {'hp': 150, 'speed': 0.5, 'size': 38, 'color': DARK_RED, 'xp': 40, 'damage': 25},
    'elite': {'hp': 75, 'speed': 1.3, 'size': 24, 'color': GOLD, 'xp': 25, 'damage': 15},
    'juggernaut': {'hp': 300, 'speed': 0.35, 'size': 48, 'color': CRIMSON, 'xp': 60, 'damage': 35},
    'behemoth': {'hp': 500, 'speed': 0.25, 'size': 58, 'color': MAROON, 'xp': 80, 'damage': 45},
    'colossus': {'hp': 800, 'speed': 0.18, 'size': 70, 'color': DARK_PURPLE, 'xp': 100, 'damage': 55},
    'titan': {'hp': 1200, 'speed': 0.12, 'size': 85, 'color': SLATE, 'xp': 130, 'damage': 65},
    'leviathan': {'hp': 2000, 'speed': 0.08, 'size': 100, 'color': STEEL, 'xp': 160, 'damage': 80}
}