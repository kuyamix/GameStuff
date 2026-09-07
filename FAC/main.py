import pygame
import sys
import math
from config import *
from utils import GameState, world_to_screen, screen_to_world, distance, clamp, is_unlocked
from entities import spawn_enemy
from abilities import start_strafe, update_strafe, start_mortar, update_mortar, start_mrls, update_mrls
from ui import UI

# ============ INITIALIZE PYGAME ============
pygame.init()

# ============ SCREEN SETUP ============
info = pygame.display.Info()
SCREEN_WIDTH = max(800, min(940, int(info.current_w * 0.7)))
SCREEN_HEIGHT = max(600, min(2030, int(info.current_h * 0.85)))

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("🎯 FAC - MRLS Support! (PC)")
clock = pygame.time.Clock()

# ============ INIT GAME ============
game = GameState()
ui = UI(game)
mouse_held = False

def reset_game():
    game.__init__()
    ui.__init__(game)

def confirm_aim():
    if game.aiming_mode:
        if game.aiming_ability == "strafe": 
            start_strafe(game)
        elif game.aiming_ability == "mortar": 
            start_mortar(game)
        elif game.aiming_ability == "mrls": 
            start_mrls(game)
        game.aiming_mode = False
        game.aiming_ability = None

def cancel_aim():
    game.aiming_mode = False
    game.aiming_ability = None

def game_over_screen():
    screen.fill(BLACK)
    
    # Game Over text
    font_huge = pygame.font.Font(None, int(ui.fonts['huge'].get_height() * 2))
    font_med = ui.fonts['medium']
    font_small = ui.fonts['small']
    
    texts = [
        (font_huge.render("💀 KIA - EVAC FAILED", True, RED), SCREEN_HEIGHT//2 - 100),
        (font_med.render(f"Level: {game.level}  Kills: {game.enemies_killed}  Time: {game.game_time//60}s", True, WHITE), SCREEN_HEIGHT//2 - 20),
        (font_small.render("Press SPACE or Click to respawn", True, WHITE), SCREEN_HEIGHT//2 + 40)
    ]
    
    for text, y in texts:
        screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, y))
    
    pygame.display.flip()
    
    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT: 
                return False
            if e.type == pygame.MOUSEBUTTONDOWN: 
                return True
            if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
                return True
        clock.tick(30)

def apply_level_up():
    game.xp = 0
    game.level += 1
    game.player_max_health += BASE_STATS['health_bonus']
    game.player_health = min(game.player_health + BASE_STATS['health_bonus'], game.player_max_health)
    game.player_speed += BASE_STATS['speed_bonus']
    
    # Check for new abilities
    new_abilities = []
    for ability, unlock_level in UNLOCK_LEVELS.items():
        if game.level == unlock_level:
            names = {'strafe': '✈️ STRAFE RUN', 'mortar': '💥 MORTAR STRIKE', 'mrls': '🚀 MRLS STRIKE'}
            new_abilities.append(names.get(ability, ability))
    
    subtext = f"HP +{BASE_STATS['health_bonus']} | Speed +{BASE_STATS['speed_bonus']:.1f}"
    if new_abilities:
        subtext += f" | 🎯 {', '.join(new_abilities)} UNLOCKED!"
    
    game.level_up_notifications.append({
        'text': f"⬆ LEVEL {game.level}!",
        'subtext': subtext,
        'timer': 120
    })

# ============ MAIN LOOP ============
running = True
while running:
    # ============ EVENT HANDLING ============
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # ===== KEYBOARD =====
        if event.type == pygame.KEYDOWN:
            # Movement
            if event.key in [pygame.K_w, pygame.K_UP]: 
                game.keys['up'] = True
            if event.key in [pygame.K_s, pygame.K_DOWN]: 
                game.keys['down'] = True
            if event.key in [pygame.K_a, pygame.K_LEFT]: 
                game.keys['left'] = True
            if event.key in [pygame.K_d, pygame.K_RIGHT]: 
                game.keys['right'] = True
            
            # Abilities
            if event.key == pygame.K_1 and is_unlocked(game.level, 'strafe'): 
                game.aiming_mode = True
                game.aiming_ability = 'strafe'
                game.aim_x, game.aim_y = game.player_x, game.player_y
            if event.key == pygame.K_2 and is_unlocked(game.level, 'mortar'): 
                game.aiming_mode = True
                game.aiming_ability = 'mortar'
                game.aim_x, game.aim_y = game.player_x, game.player_y
            if event.key == pygame.K_3 and is_unlocked(game.level, 'mrls'): 
                game.aiming_mode = True
                game.aiming_ability = 'mrls'
                game.aim_x, game.aim_y = game.player_x, game.player_y
            
            # Other keys
            if event.key == pygame.K_ESCAPE: 
                cancel_aim()
            if event.key == pygame.K_r: 
                reset_game()
            if event.key == pygame.K_SPACE and game.xp >= game.xp_to_next:
                apply_level_up()
            if event.key in [pygame.K_PLUS, pygame.K_EQUALS]: 
                game.zoom_level = min(game.zoom_level + 0.05, 2.0)
            if event.key == pygame.K_MINUS: 
                game.zoom_level = max(game.zoom_level - 0.05, 0.25)
        
        if event.type == pygame.KEYUP:
            if event.key in [pygame.K_w, pygame.K_UP]: 
                game.keys['up'] = False
            if event.key in [pygame.K_s, pygame.K_DOWN]: 
                game.keys['down'] = False
            if event.key in [pygame.K_a, pygame.K_LEFT]: 
                game.keys['left'] = False
            if event.key in [pygame.K_d, pygame.K_RIGHT]: 
                game.keys['right'] = False
        
        # ===== MOUSE =====
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            
            # Right click cancel
            if event.button == 3 and game.aiming_mode:
                cancel_aim()
                continue
            
            # Scroll zoom
            if event.button == 4:  # Scroll up
                game.zoom_level = min(game.zoom_level + 0.05, 2.0)
                continue
            if event.button == 5:  # Scroll down
                game.zoom_level = max(game.zoom_level - 0.05, 0.25)
                continue
            
            # Upgrade button
            if game.xp >= game.xp_to_next and ui.upgrade_btn.collidepoint(x, y):
                apply_level_up()
                continue
            
            # Ability buttons
            if ui.strafe_btn.collidepoint(x, y):
                if game.aiming_mode: 
                    confirm_aim()
                elif is_unlocked(game.level, 'strafe'): 
                    game.aiming_mode = True
                    game.aiming_ability = 'strafe'
                    game.aim_x, game.aim_y = game.player_x, game.player_y
                continue
            
            if ui.mortar_btn.collidepoint(x, y):
                if game.aiming_mode: 
                    confirm_aim()
                elif is_unlocked(game.level, 'mortar'): 
                    game.aiming_mode = True
                    game.aiming_ability = 'mortar'
                    game.aim_x, game.aim_y = game.player_x, game.player_y
                continue
            
            if ui.mrls_btn.collidepoint(x, y):
                if game.aiming_mode: 
                    confirm_aim()
                elif is_unlocked(game.level, 'mrls'): 
                    game.aiming_mode = True
                    game.aiming_ability = 'mrls'
                    game.aim_x, game.aim_y = game.player_x, game.player_y
                continue
            
            # Cancel button (when aiming)
            if game.aiming_mode and ui.cancel_btn.collidepoint(x, y):
                cancel_aim()
                continue
            
            # Zoom buttons
            if ui.zoom_in.collidepoint(x, y):
                game.zoom_level = min(game.zoom_level + 0.05, 2.0)
                continue
            if ui.zoom_out.collidepoint(x, y):
                game.zoom_level = max(game.zoom_level - 0.05, 0.25)
                continue
            
            # Aiming click
            if game.aiming_mode:
                game.aim_x, game.aim_y = screen_to_world(x, y, game.camera_x, game.camera_y, game.zoom_level)
                game.aim_x = clamp(game.aim_x, 0, MAP_WIDTH)
                game.aim_y = clamp(game.aim_y, 0, MAP_HEIGHT)
                confirm_aim()
            else:
                mouse_held = True
        
        if event.type == pygame.MOUSEBUTTONUP:
            mouse_held = False
        
        if event.type == pygame.MOUSEMOTION:
            if game.aiming_mode and mouse_held:
                game.aim_x, game.aim_y = screen_to_world(event.pos[0], event.pos[1], game.camera_x, game.camera_y, game.zoom_level)
                game.aim_x = clamp(game.aim_x, 0, MAP_WIDTH)
                game.aim_y = clamp(game.aim_y, 0, MAP_HEIGHT)
    
    # ============ UPDATE ============
    game.game_time += 1
    
    # ----- Player Movement -----
    move_mult = 0.6 if game.aiming_mode else 1.0
    dx = dy = 0
    if game.keys['up']: dy -= 1
    if game.keys['down']: dy += 1
    if game.keys['left']: dx -= 1
    if game.keys['right']: dx += 1
    
    if dx or dy:
        length = math.hypot(dx, dy)
        game.player_x += (dx / length) * game.player_speed * move_mult
        game.player_y += (dy / length) * game.player_speed * move_mult
    
    game.player_x = clamp(game.player_x, 0, MAP_WIDTH)
    game.player_y = clamp(game.player_y, 0, MAP_HEIGHT)
    
    # ----- Camera -----
    game.camera_x += (game.player_x - game.camera_x) * 0.08
    game.camera_y += (game.player_y - game.camera_y) * 0.08
    
    # ----- Cooldowns -----
    if game.strafe_cooldown > 0: game.strafe_cooldown -= 1
    if game.mortar_cooldown > 0: game.mortar_cooldown -= 1
    if game.mrls_cooldown > 0: game.mrls_cooldown -= 1
    
    # ----- Abilities -----
    if game.strafe_active: update_strafe(game)
    if game.mortar_phase or game.mortar_flash or game.mortar_impact_effects: 
        update_mortar(game)
    if game.mrls_active: update_mrls(game)
    
    # ----- Spawn Enemies -----
    game.enemy_spawn_timer += 1
    delay = max(10, 35 - game.game_time // 300)
    if game.enemy_spawn_timer >= delay and len(game.enemies) < 60:
        game.enemy_spawn_timer = 0
        spawn_enemy(game)
    
    # ----- Update Enemies -----
    for enemy in game.enemies[:]:
        enemy.move_towards_player(game.player_x, game.player_y)
        
        if distance(enemy.x, enemy.y, game.player_x, game.player_y) < (enemy.size + 22) / 2:
            if enemy.attack_cooldown == 0:
                game.player_health -= enemy.damage
                enemy.attack_cooldown = 40
                
                # Knockback
                dx = enemy.x - game.player_x
                dy = enemy.y - game.player_y
                dist = math.hypot(dx, dy)
                if dist > 0:
                    enemy.knockback_x = (dx / dist) * 20
                    enemy.knockback_y = (dy / dist) * 20
                
                if game.player_health <= 0:
                    if game_over_screen():
                        reset_game()
                    else:
                        running = False
                    break
    
    # ----- Update Gems -----
    for gem in game.gems[:]:
        gem.update(game.player_x, game.player_y)
        player_rect = pygame.Rect(game.player_x - 12, game.player_y - 12, 24, 24)
        if gem.rect.colliderect(player_rect):
            game.xp += gem.value
            game.gems.remove(gem)
            if game.xp >= game.xp_to_next:
                apply_level_up()
    
    # ============ DRAW ============
    screen.fill(BLACK)
    
    # ----- Grid -----
    gs = 100
    sx = int(game.camera_x - SCREEN_WIDTH/2/game.zoom_level)
    ex = int(game.camera_x + SCREEN_WIDTH/2/game.zoom_level)
    sy = int(game.camera_y - SCREEN_HEIGHT/2/game.zoom_level)
    ey = int(game.camera_y + SCREEN_HEIGHT/2/game.zoom_level)
    
    for x in range(sx - sx % gs, ex + gs, gs):
        px, _ = world_to_screen(x, 0, game.camera_x, game.camera_y, game.zoom_level)
        if 0 <= px <= SCREEN_WIDTH:
            pygame.draw.line(screen, (30, 35, 45), (px, 0), (px, SCREEN_HEIGHT), 1)
    
    for y in range(sy - sy % gs, ey + gs, gs):
        _, py = world_to_screen(0, y, game.camera_x, game.camera_y, game.zoom_level)
        if 0 <= py <= SCREEN_HEIGHT:
            pygame.draw.line(screen, (30, 35, 45), (0, py), (SCREEN_WIDTH, py), 1)
    
    # ----- Draw Strafe -----
    if game.strafe_active:
        cx, cy = world_to_screen(game.strafe_x, game.strafe_y, game.camera_x, game.camera_y, game.zoom_level)
        sx1 = cx + math.cos(game.strafe_angle + math.pi/2) * 300 * game.zoom_level
        sy1 = cy + math.sin(game.strafe_angle + math.pi/2) * 300 * game.zoom_level
        ex1 = cx + math.cos(game.strafe_angle - math.pi/2) * 300 * game.zoom_level
        ey1 = cy + math.sin(game.strafe_angle - math.pi/2) * 300 * game.zoom_level
        pygame.draw.line(screen, (255, 255, 100), (sx1, sy1), (ex1, ey1), 2)
        
        for b in game.strafe_bullets:
            px, py = world_to_screen(b['x'], b['y'], game.camera_x, game.camera_y, game.zoom_level)
            size = int(4 * (b['life'] / 20) * game.zoom_level)
            if size > 0:
                pygame.draw.circle(screen, (255, 255, 200), (int(px), int(py)), size)
        
        for p in game.strafe_particles:
            px, py = world_to_screen(p['x'], p['y'], game.camera_x, game.camera_y, game.zoom_level)
            alpha = p['life'] / 30
            size = int(p['size'] * alpha * game.zoom_level)
            if size > 0:
                pygame.draw.circle(screen, (255, int(p['color'][1] * alpha), 0), (int(px), int(py)), size)
    
    # ----- Draw Mortar -----
    if game.mortar_phase == 1:
        px, py = world_to_screen(game.mortar_target_x, game.mortar_target_y, game.camera_x, game.camera_y, game.zoom_level)
        pygame.draw.circle(screen, RED, (int(px), int(py)), int(18 * game.zoom_level), 3)
        warning = ui.fonts['big'].render("⚠️ INCOMING!", True, RED)
        screen.blit(warning, (px - 80, py - 80))
        
        for shell in game.mortar_shells:
            sx, sy = world_to_screen(shell['x'], shell['y'], game.camera_x, game.camera_y, game.zoom_level)
            pygame.draw.circle(screen, ORANGE, (int(sx), int(sy)), int(12 * game.zoom_level))
    
    if game.mortar_flash > 0:
        px, py = world_to_screen(game.mortar_target_x, game.mortar_target_y, game.camera_x, game.camera_y, game.zoom_level)
        r = 160 * game.zoom_level * (game.mortar_flash / 25)
        pygame.draw.circle(screen, (255, 200, 100), (int(px), int(py)), int(r))
        pygame.draw.circle(screen, WHITE, (int(px), int(py)), int(r), int(5 * game.zoom_level))
    
    for e in game.mortar_impact_effects:
        px, py = world_to_screen(e['x'], e['y'], game.camera_x, game.camera_y, game.zoom_level)
        size = int(e['size'] * (e['life'] / 35) * game.zoom_level)
        if size > 0:
            pygame.draw.circle(screen, (255, int(150 * e['life']/35), int(50 * e['life']/35)), (int(px), int(py)), size)
    
    # ----- Draw MRLS -----
    if game.mrls_active:
        if game.mrls_warning_timer > 0:
            px, py = world_to_screen(game.mrls_target_x, game.mrls_target_y, game.camera_x, game.camera_y, game.zoom_level)
            pulse = math.sin(game.mrls_warning_timer * 0.3) * 0.3 + 0.7
            r = 250 * game.zoom_level * pulse
            pygame.draw.circle(screen, (255, 50, 50), (int(px), int(py)), int(r), 3)
            
            txt = "⚠️ MRLS INCOMING!" if game.mrls_warning_timer > 25 else "💥 IMPACT!"
            color = RED if game.mrls_warning_timer > 25 else YELLOW
            warning = ui.fonts['big'].render(txt, True, color)
            screen.blit(warning, (px - 100, py - 100))
        
        for rocket in game.mrls_rockets:
            for trail in rocket['trail']:
                px, py = world_to_screen(trail['x'], trail['y'], game.camera_x, game.camera_y, game.zoom_level)
                size = int(5 * (trail['life'] / 10) * game.zoom_level)
                if size > 0:
                    pygame.draw.circle(screen, (255, 200, 100), (int(px), int(py)), size)
            
            if rocket['active'] and not rocket['impacted']:
                px, py = world_to_screen(rocket['x'], rocket['y'], game.camera_x, game.camera_y, game.zoom_level)
                size = int(10 * game.zoom_level)
                pygame.draw.circle(screen, (255, 200, 50), (int(px), int(py)), size + 4)
                pygame.draw.circle(screen, (255, 220, 80), (int(px), int(py)), size)
                pygame.draw.circle(screen, (255, 100, 0), (int(px - 6*game.zoom_level), int(py + 6*game.zoom_level)), int(size * 0.9))
        
        for e in game.mrls_explosions:
            px, py = world_to_screen(e['x'], e['y'], game.camera_x, game.camera_y, game.zoom_level)
            size = int(e['size'] * (e['life'] / 20) * game.zoom_level)
            if size > 0:
                pygame.draw.circle(screen, e['color'], (int(px), int(py)), size)
                if size > 2:
                    pygame.draw.circle(screen, (255, 255, 200), (int(px), int(py)), int(size * 1.3))
        
        if game.mrls_flash > 0:
            px, py = world_to_screen(game.mrls_target_x, game.mrls_target_y, game.camera_x, game.camera_y, game.zoom_level)
            r = game.mrls_flash * 10 * game.zoom_level
            pygame.draw.circle(screen, (255, 255, 200), (int(px), int(py)), int(r))
            pygame.draw.circle(screen, (255, 255, 255), (int(px), int(py)), int(r * 0.4))
    
    # ----- Draw Enemies -----
    for enemy in game.enemies:
        enemy.draw(screen, game.camera_x, game.camera_y, game.zoom_level)
    
    # ----- Draw Gems -----
    for gem in game.gems:
        gem.draw(screen, game.camera_x, game.camera_y, game.zoom_level)
    
    # ----- Draw Player -----
    px, py = world_to_screen(game.player_x, game.player_y, game.camera_x, game.camera_y, game.zoom_level)
    pygame.draw.circle(screen, (50, 150, 50), (int(px), int(py)), int(16 * game.zoom_level))
    pygame.draw.circle(screen, GREEN, (int(px), int(py)), int(12 * game.zoom_level))
    pygame.draw.circle(screen, WHITE, (int(px + 7*game.zoom_level), int(py + 7*game.zoom_level)), int(4 * game.zoom_level))
    pygame.draw.circle(screen, WHITE, (int(px + 17*game.zoom_level), int(py + 7*game.zoom_level)), int(4 * game.zoom_level))
    
    # ----- UI -----
    ui.draw(screen)
    ui.draw_notifications(screen)
    
    # ============ DISPLAY ============
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()