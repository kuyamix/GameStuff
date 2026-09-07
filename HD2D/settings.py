import pygame

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
DARK_GREEN = (30, 60, 30)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (150, 150, 150)
BROWN = (101, 67, 33)
BLOOD_RED = (139, 0, 0)
CYAN = (0, 255, 255)

# Player settings
PLAYER_SPEED = 250
PLAYER_SPRINT_MULTIPLIER = 1.6
PLAYER_MAX_HEALTH = 100
PLAYER_MAX_STAMINA = 100
PLAYER_RADIUS = 12
PLAYER_DIVE_SPEED = 600
PLAYER_DIVE_DURATION = 0.3

# Weapon settings
WEAPON_SETTINGS = {
    'rifle': {
        'damage': 25,
        'fire_rate': 0.12,
        'bullet_speed': 800,
        'spread': 0.04,
        'ammo': 30,
        'reload_time': 1.5,
        'pellets': 1,
        'color': YELLOW
    },
    'shotgun': {
        'damage': 12,
        'fire_rate': 0.8,
        'bullet_speed': 500,
        'spread': 0.25,
        'ammo': 8,
        'reload_time': 2.0,
        'pellets': 6,
        'color': ORANGE
    },
    'laser': {
        'damage': 15,
        'fire_rate': 0.05,
        'bullet_speed': 1000,
        'spread': 0.0,
        'ammo': float('inf'),
        'reload_time': 0,
        'pellets': 1,
        'color': CYAN
    },
    'smg': {
        'damage': 10,
        'fire_rate': 0.06,
        'bullet_speed': 700,
        'spread': 0.08,
        'ammo': 50,
        'reload_time': 1.2,
        'pellets': 1,
        'color': WHITE
    }
}

# Enemy settings
ENEMY_SETTINGS = {
    'scavenger': {
        'health': 30,
        'speed': 180,
        'damage': 10,
        'radius': 8,
        'color': (150, 200, 50),
        'score': 10
    },
    'warrior': {
        'health': 80,
        'speed': 120,
        'damage': 25,
        'radius': 14,
        'color': (180, 150, 50),
        'score': 25
    },
    'charger': {
        'health': 250,
        'speed': 80,
        'damage': 40,
        'radius': 25,
        'color': (200, 100, 50),
        'score': 100
    },
    'spewer': {
        'health': 60,
        'speed': 100,
        'damage': 15,
        'radius': 16,
        'color': (150, 50, 200),
        'score': 50
    },
    'stalker': {
        'health': 50,
        'speed': 250,
        'damage': 20,
        'radius': 10,
        'color': (100, 100, 100),
        'score': 75
    }
}

# Stratagem settings
STRATAGEM_CODES = {
    'airstrike': [pygame.K_UP, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT],
    'supply': [pygame.K_DOWN, pygame.K_DOWN, pygame.K_UP, pygame.K_UP],
    'turret': [pygame.K_DOWN, pygame.K_UP, pygame.K_RIGHT, pygame.K_LEFT],
    'orbital_laser': [pygame.K_UP, pygame.K_RIGHT, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT],
    'reinforce': [pygame.K_UP, pygame.K_DOWN, pygame.K_RIGHT, pygame.K_LEFT, pygame.K_UP]
}

STRATAGEM_COOLDOWNS = {
    'airstrike': 10.0,
    'supply': 20.0,
    'turret': 15.0,
    'orbital_laser': 25.0,
    'reinforce': 30.0
}

# Wave settings
WAVE_INTERVAL = 5.0
BASE_ENEMIES_PER_WAVE = 5
ENEMIES_PER_WAVE_INCREMENT = 3