import pygame
from constants import *

def draw_ui(screen, game, font, small_font, large_font, title_font, ui_font, small_bold_font):
    # Top status bar
    top_h = 112
    top = pygame.Surface((SCREEN_WIDTH, top_h), pygame.SRCALPHA)
    top.fill((*PANEL, 235))
    screen.blit(top, (0, 0))
    pygame.draw.line(screen, BORDER, (0, top_h - 1), (SCREEN_WIDTH, top_h - 1), 2)

    # Title / status
    title = title_font.render("BASE DEFENSE", True, WHITE)
    screen.blit(title, (22, 12))
    status = "DEFENDING" if not game.game_over else "BASE LOST"
    status_color = SUCCESS if not game.game_over else RED
    status_text = small_bold_font.render(status, True, status_color)
    screen.blit(status_text, (24, 52))

    # Wave Started Message
    if game.wave_started_message_timer > 0:
        wave_msg = font.render("WAVE STARTED!", True, YELLOW)
        screen.blit(wave_msg, (SCREEN_WIDTH // 2 - 100, 20))

    # Compact stat cards
    cards = [
        (155, "GOLD", f"{game.gold}", YELLOW),
        (300, "WAVE", f"{game.wave}", WHITE),
        (445, "BASE HP", f"{game.base.health}/{game.base.max_health}", SUCCESS if game.base.health > 120 else WARNING),
        (625, "KILLS", f"{game.kills}", WHITE),
        (770, "ENEMIES", f"{len(game.enemies)}", ORANGE),
    ]
    for x, label, value, value_color in cards:
        card = pygame.Rect(x, 15, 130 if label not in ("BASE HP",) else 160, 78)
        pygame.draw.rect(screen, PANEL_LIGHT, card, border_radius=8)
        pygame.draw.rect(screen, BORDER, card, 1, border_radius=8)
        label_surface = small_font.render(label, True, TEXT_MUTED)
        value_surface = ui_font.render(value, True, value_color)
        screen.blit(label_surface, (card.x + 10, card.y + 8))
        screen.blit(value_surface, (card.x + 10, card.y + 37))

    # Zoom + current mode
    zoom_text = small_font.render(f"Zoom {game.camera.zoom:.1f}x", True, TEXT_MUTED)
    screen.blit(zoom_text, (SCREEN_WIDTH - 175, 18))
    mode = "TOWER" if game.placing_tower else "ARTILLERY" if game.artillery_mode else "STRAFE" if game.strafe_mode else "SELECT"
    mode_color = SUCCESS if game.placing_tower else RED if game.artillery_mode else CYAN if game.strafe_mode else TEXT_MUTED
    mode_surface = ui_font.render(mode, True, mode_color)
    screen.blit(mode_surface, (SCREEN_WIDTH - 175, 47))

    # Wave countdown
    if not game.game_over:
        if game.wave_in_progress:
            progress = max(0, game.horde_size)
            wave_label = f"WAVE {game.wave}  •  {progress} TO SPAWN"
            wave_color = ORANGE
        else:
            seconds = max(0, game.wave_timer // FPS + 1)
            wave_label = f"NEXT WAVE IN {seconds}s"
            wave_color = WARNING
        wave_surface = small_bold_font.render(wave_label, True, wave_color)
        screen.blit(wave_surface, (SCREEN_WIDTH - 430, 82))

    # Bottom command bar
    bottom_h = 116
    bottom_y = SCREEN_HEIGHT - bottom_h
    bottom = pygame.Surface((SCREEN_WIDTH, bottom_h), pygame.SRCALPHA)
    bottom.fill((*PANEL, 238))
    screen.blit(bottom, (0, bottom_y))
    pygame.draw.line(screen, BORDER, (0, bottom_y), (SCREEN_WIDTH, bottom_y), 2)

    # Mode cards
    controls = [
        ("1", "TOWER", f"{TOWER_COST}G", game.placing_tower, GREEN),
        ("2", "ARTILLERY", f"{ARTILLERY_COST}G", game.artillery_mode, RED),
        ("3", "STRAFE", f"{STRAFE_COST}G", game.strafe_mode, CYAN),
    ]
    x = 20
    for key, name, cost, active, accent in controls:
        w = 170 if name == "ARTILLERY" else 145
        rect = pygame.Rect(x, bottom_y + 12, w, 56)
        pygame.draw.rect(screen, PANEL_LIGHT if not active else (45, 55, 45), rect, border_radius=7)
        pygame.draw.rect(screen, accent if active else BORDER, rect, 2 if active else 1, border_radius=7)
        key_rect = pygame.Rect(rect.x + 7, rect.y + 7, 34, 42)
        pygame.draw.rect(screen, accent, key_rect, border_radius=6)
        key_text = ui_font.render(key, True, BLACK)
        screen.blit(key_text, key_text.get_rect(center=key_rect.center))
        screen.blit(small_bold_font.render(name, True, WHITE), (rect.x + 49, rect.y + 7))
        screen.blit(small_font.render(cost, True, YELLOW), (rect.x + 49, rect.y + 30))
        x += w + 10

    # Help controls
    help_lines = [
        "WASD / Arrows  Camera",
        "Mouse Wheel  Zoom",
        "SPACE  Start Wave",
        "C  Center Base   ESC  Quit",
    ]
    hx = SCREEN_WIDTH - 470
    for i, line in enumerate(help_lines):
        t = small_font.render(line, True, TEXT_MUTED)
        screen.blit(t, (hx, bottom_y + 9 + i * 24))

    # Mode hint
    if game.placing_tower:
        hint = f"CLICK TO PLACE TOWER  •  ESCAPE/1 TO CANCEL"
    elif game.artillery_mode:
        hint = f"CLICK A TARGET AREA FOR ARTILLERY  •  {ARTILLERY_COST} GOLD"
    elif game.strafe_mode:
        hint = f"CLICK TO CALL A STRAFING RUN  •  {STRAFE_COST} GOLD"
    else:
        hint = "1 TOWER   2 ARTILLERY   3 STRAFE   •   CLICK TO USE"
    hint_surface = small_bold_font.render(hint, True, ACCENT)
    screen.blit(hint_surface, (20, bottom_y + 82))

    # Game over overlay
    if game.game_over:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        screen.blit(overlay, (0, 0))

        panel = pygame.Rect(SCREEN_WIDTH // 2 - 300, SCREEN_HEIGHT // 2 - 180, 600, 360)
        pygame.draw.rect(screen, PANEL, panel, border_radius=16)
        pygame.draw.rect(screen, RED, panel, 3, border_radius=16)
        game_over_text = large_font.render("BASE DESTROYED", True, RED)
        screen.blit(game_over_text, game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 95)))
        final_wave_text = font.render(f"Waves survived: {game.wave - 1}", True, WHITE)
        screen.blit(final_wave_text, final_wave_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 25)))
        kills_text = font.render(f"Total kills: {game.kills}", True, WHITE)
        screen.blit(kills_text, kills_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 20)))
        restart_text = font.render("Press R to restart", True, YELLOW)
        screen.blit(restart_text, restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 90)))