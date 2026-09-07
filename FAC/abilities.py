import random
import math
from config import *
from utils import distance, is_unlocked
from entities import Gem

# ============ STRAFE ============
def start_strafe(game):
    if game.strafe_cooldown > 0: return False
    game.strafe_active = True
    game.strafe_x, game.strafe_y = game.aim_x, game.aim_y
    game.strafe_duration = 60
    game.strafe_cooldown = max(60, int(300 * (1.0 - (game.level - 1) * 0.02)))
    game.strafe_pass = 0
    game.strafe_particles = []
    game.strafe_bullets = []
    # Find best approach angle
    edges = [(game.aim_x, 0, -math.pi/2), (game.aim_x, MAP_HEIGHT, math.pi/2),
             (0, game.aim_y, math.pi), (MAP_WIDTH, game.aim_y, 0)]
    game.strafe_angle = min(edges, key=lambda e: abs(e[0] - game.aim_x) + abs(e[1] - game.aim_y))[2]
    return True

def update_strafe(game):
    if not game.strafe_active: return
    damage = 35 + game.level * 2
    game.strafe_pass += 1
    
    for i in range(20):
        progress = i / 20
        offset = (progress - 0.5) * 300
        x = game.strafe_x + math.cos(game.strafe_angle + math.pi/2) * offset + random.uniform(-10, 10)
        y = game.strafe_y + math.sin(game.strafe_angle + math.pi/2) * offset + random.uniform(-10, 10)
        
        for enemy in game.enemies[:]:
            if distance(enemy.x, enemy.y, x, y) < 50:
                enemy.hp -= damage
                enemy.knockback_x = math.cos(game.strafe_angle) * 30
                enemy.knockback_y = math.sin(game.strafe_angle) * 30
                enemy.hit_timer = 15
                if enemy.hp <= 0:
                    game.gems.append(Gem(enemy.x, enemy.y, enemy.xp_value))
                    game.enemies.remove(enemy)
                    game.enemies_killed += 1
        
        game.strafe_bullets.append({
            'x': x, 'y': y, 'life': 20,
            'vx': math.cos(game.strafe_angle) * random.uniform(5, 10),
            'vy': math.sin(game.strafe_angle) * random.uniform(5, 10)
        })
        game.strafe_particles.append({
            'x': x, 'y': y, 'life': 30,
            'color': (255, random.randint(150, 255), 0),
            'size': random.randint(3, 10)
        })
    
    # Update particles
    for b in game.strafe_bullets[:]:
        b['x'] += b['vx']; b['y'] += b['vy']; b['life'] -= 1
        if b['life'] <= 0: game.strafe_bullets.remove(b)
    for p in game.strafe_particles[:]:
        p['life'] -= 1; p['x'] += random.uniform(-3, 3); p['y'] += random.uniform(-3, 3)
        if p['life'] <= 0: game.strafe_particles.remove(p)
    
    game.strafe_duration -= 1
    if game.strafe_duration <= 0:
        game.strafe_active = False
        game.strafe_particles.clear()
        game.strafe_bullets.clear()

# ============ MORTAR ============
def start_mortar(game):
    if game.mortar_cooldown > 0 or not is_unlocked(game.level, 'mortar'): return False
    game.mortar_phase = 1
    game.mortar_target_x, game.mortar_target_y = game.aim_x, game.aim_y
    game.mortar_impact_timer = 55
    game.mortar_cooldown = max(80, int(400 * (1.0 - (game.level - 1) * 0.02)))
    game.mortar_shells = []
    for i in range(6):
        angle, dist = random.uniform(0, 2*math.pi), random.uniform(20, 100)
        game.mortar_shells.append({
            'x': game.aim_x + math.cos(angle) * dist * 0.2,
            'y': -60 - i * 25,
            'target_x': game.aim_x + math.cos(angle) * dist * 0.6,
            'target_y': game.aim_y + math.sin(angle) * dist * 0.6,
            'speed': 5 + i * 0.5
        })
    return True

def update_mortar(game):
    if game.mortar_phase == 1:
        game.mortar_impact_timer -= 1
        for shell in game.mortar_shells[:]:
            shell['y'] += shell['speed']
            if shell['y'] > shell['target_y']:
                game.mortar_shells.remove(shell)
        if game.mortar_impact_timer <= 0:
            # Impact
            damage = 60 + game.level * 4
            for enemy in game.enemies[:]:
                dist = distance(enemy.x, enemy.y, game.mortar_target_x, game.mortar_target_y)
                if dist < 160:
                    enemy.hp -= damage * (1 - (dist / 160) * 0.3)
                    if dist > 0:
                        enemy.knockback_x = (enemy.x - game.mortar_target_x) / dist * 30
                        enemy.knockback_y = (enemy.y - game.mortar_target_y) / dist * 30
                    enemy.hit_timer = 20
                    if enemy.hp <= 0:
                        game.gems.append(Gem(enemy.x, enemy.y, enemy.xp_value))
                        game.enemies.remove(enemy)
                        game.enemies_killed += 1
            game.mortar_flash = 25
            game.mortar_phase = 0
            game.mortar_impact_effects = []
            for _ in range(60):
                angle, dist = random.uniform(0, 2*math.pi), random.uniform(0, 160)
                game.mortar_impact_effects.append({
                    'x': game.mortar_target_x + math.cos(angle) * dist,
                    'y': game.mortar_target_y + math.sin(angle) * dist,
                    'life': 35 + random.randint(0, 20),
                    'vx': math.cos(angle) * random.uniform(2, 12),
                    'vy': math.sin(angle) * random.uniform(2, 12) - 5,
                    'size': random.randint(3, 12)
                })
            game.mortar_shells.clear()
    
    if game.mortar_flash > 0: game.mortar_flash -= 1
    for e in game.mortar_impact_effects[:]:
        e['x'] += e['vx']; e['y'] += e['vy']; e['vy'] += 0.2; e['life'] -= 1
        if e['life'] <= 0: game.mortar_impact_effects.remove(e)

# ============ MRLS (UPDATED - Faster Impact + Wider Spread) ============
def start_mrls(game):
    if game.mrls_cooldown > 0 or not is_unlocked(game.level, 'mrls'): return False
    
    game.mrls_active = True
    game.mrls_target_x, game.mrls_target_y = game.aim_x, game.aim_y
    game.mrls_phase = 1
    game.mrls_warning_timer = 20  # REDUCED from 40 to 20 (faster warning)
    game.mrls_flash = 0
    game.mrls_rockets = []
    game.mrls_explosions = []
    
    # WIDER SPREAD - increased from 250 to 400
    spread_radius = 400 + game.level * 10  # Scales with level
    
    for i in range(game.mrls_total_rockets):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0, spread_radius)  # Wider spread
        tx = game.aim_x + math.cos(angle) * dist
        ty = game.aim_y + math.sin(angle) * dist
        
        # Clamp to map boundaries
        tx = max(0, min(tx, MAP_WIDTH))
        ty = max(0, min(ty, MAP_HEIGHT))
        
        game.mrls_rockets.append({
            'x': tx + random.uniform(-200, 200),  # More variation in start
            'y': -50 - random.randint(0, 80),
            'target_x': tx,
            'target_y': ty,
            'speed': random.uniform(30, 45),  # FASTER - increased from 20-30
            'trail': [],
            'active': True,
            'impacted': False
        })
    
    game.mrls_cooldown = max(140, int(700 * (1.0 - (game.level - 1) * 0.02)))
    return True

def create_mrls_explosion(game, x, y):
    # BIGGER EXPLOSION RADIUS
    radius = 150 + game.level * 3  # Increased from 120
    damage = 70 + game.level * 6    # Increased from 60
    
    for enemy in game.enemies[:]:
        dist = distance(x, y, enemy.x, enemy.y)
        if dist < radius:
            # More damage at center, less at edge
            damage_mult = 1 - (dist / radius) * 0.2  # Less falloff (was 0.3)
            enemy.hp -= damage * damage_mult
            if dist > 0:
                # Stronger knockback
                enemy.knockback_x = (enemy.x - x) / dist * 50
                enemy.knockback_y = (enemy.y - y) / dist * 50
            enemy.hit_timer = 25
            if enemy.hp <= 0:
                game.gems.append(Gem(enemy.x, enemy.y, enemy.xp_value))
                game.enemies.remove(enemy)
                game.enemies_killed += 1
    
    game.mrls_flash = 25  # Slightly longer flash
    
    # MORE EXPLOSION PARTICLES
    for _ in range(50):  # Increased from 30
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0, radius * 0.9)
        game.mrls_explosions.append({
            'x': x + math.cos(angle) * dist,
            'y': y + math.sin(angle) * dist,
            'life': 20 + random.randint(0, 20),  # Longer life
            'vx': math.cos(angle) * random.uniform(3, 14),
            'vy': math.sin(angle) * random.uniform(3, 14) - 4,
            'size': random.randint(4, 18),  # Bigger particles
            'color': random.choice([
                (255, 200, 50),   # Gold
                (255, 150, 20),   # Orange
                (255, 100, 0),    # Red-orange
                (255, 255, 100),  # Light yellow
                (255, 50, 50),    # Bright red
                (255, 200, 150)   # Light orange
            ])
        })

def update_mrls(game):
    if not game.mrls_active: return
    
    # FASTER WARNING COUNTDOWN
    if game.mrls_warning_timer > 0:
        game.mrls_warning_timer -= 1
    
    if game.mrls_phase == 1:
        all_impacted = True
        for rocket in game.mrls_rockets:
            if rocket['active'] and not rocket['impacted']:
                all_impacted = False
                dx, dy = rocket['target_x'] - rocket['x'], rocket['target_y'] - rocket['y']
                dist = math.hypot(dx, dy)
                if dist > 5:
                    # FASTER MOVEMENT
                    speed = rocket['speed']
                    rocket['x'] += (dx / dist) * speed
                    rocket['y'] += (dy / dist) * speed * 0.5 - 0.5  # Less gravity
                    
                    # More trail particles
                    rocket['trail'].append({'x': rocket['x'], 'y': rocket['y'], 'life': 12})
                    if len(rocket['trail']) > 20:  # Longer trail
                        rocket['trail'].pop(0)
                else:
                    rocket['impacted'] = True
                    rocket['active'] = False
                    create_mrls_explosion(game, rocket['target_x'], rocket['target_y'])
        
        # Update trails
        for rocket in game.mrls_rockets:
            for trail in rocket['trail'][:]:
                trail['life'] -= 1
                if trail['life'] <= 0:
                    rocket['trail'].remove(trail)
        
        if all_impacted:
            game.mrls_phase = 2
            game.mrls_flash = 40  # Bigger flash
    
    elif game.mrls_phase == 2:
        if game.mrls_flash > 0:
            game.mrls_flash -= 1
        
        # Update explosion particles
        for e in game.mrls_explosions[:]:
            e['x'] += e['vx']
            e['y'] += e['vy']
            e['vy'] += 0.15  # Less gravity for bigger spread
            e['life'] -= 1
            if e['life'] <= 0:
                game.mrls_explosions.remove(e)
        
        if not game.mrls_explosions and game.mrls_flash == 0:
            game.mrls_active = False
            game.mrls_phase = 0
            game.mrls_rockets.clear()