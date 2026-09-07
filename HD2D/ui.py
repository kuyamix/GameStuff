import pygame
import math
from settings import *

class UI:
    def __init__(self):
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_large = pygame.font.Font(None, 72)
        self.font_huge = pygame.font.Font(None, 120)
        
    def draw_hud(self, screen, player, score, wave, game_time, stratagem_system):
        # Draw health bar
        health_bar_width = 200
        health_bar_height = 20
        health_bar_x = 20
        health_bar_y = 20
        
        # Background
        pygame.draw.rect(screen, DARK_GRAY, 
                        (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        
        # Health
        health_percent = player.health / player.max_health
        health_color = GREEN if health_percent > 0.5 else (YELLOW if health_percent > 0.25 else RED)
        pygame.draw.rect(screen, health_color, 
                        (health_bar_x, health_bar_y, 
                         health_bar_width * health_percent, health_bar_height))
        
        # Health text
        health_text = self.font_small.render(f"HP: {int(player.health)}/{player.max_health}", 
                                             True, WHITE)
        screen.blit(health_text, (health_bar_x, health_bar_y + 25))
        
        # Draw stamina bar
        stamina_bar_width = 150
        stamina_bar_height = 10
        stamina_bar_x = 20
        stamina_bar_y = 50
        
        pygame.draw.rect(screen, DARK_GRAY, 
                        (stamina_bar_x, stamina_bar_y, stamina_bar_width, stamina_bar_height))
        stamina_percent = player.stamina / PLAYER_MAX_STAMINA
        pygame.draw.rect(screen, YELLOW, 
                        (stamina_bar_x, stamina_bar_y, 
                         stamina_bar_width * stamina_percent, stamina_bar_height))
        
        # Draw weapon info
        weapon_text = self.font_small.render(f"WEAPON: {player.weapon.type.upper()}", 
                                             True, WHITE)
        screen.blit(weapon_text, (20, 70))
        
        if player.weapon.type != 'laser':
            ammo_text = self.font_small.render(f"AMMO: {player.weapon.ammo}/{player.weapon.max_ammo}", 
                                               True, WHITE)
            screen.blit(ammo_text, (20, 90))
            
            if player.weapon.reloading:
                reload_text = self.font_small.render("RELOADING...", True, RED)
                screen.blit(reload_text, (20, 110))
        
        # Draw grenades
        grenade_text = self.font_small.render(f"GRENADES: {player.grenades}", True, WHITE)
        screen.blit(grenade_text, (20, 130))
        
        # Draw score
        score_text = self.font_medium.render(f"SCORE: {score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH - 200, 20))
        
        # Draw wave
        wave_text = self.font_medium.render(f"WAVE: {wave}", True, WHITE)
        screen.blit(wave_text, (SCREEN_WIDTH - 200, 60))
        
        # Draw time
        minutes = int(game_time // 60)
        seconds = int(game_time % 60)
        time_text = self.font_small.render(f"TIME: {minutes:02d}:{seconds:02d}", True, WHITE)
        screen.blit(time_text, (SCREEN_WIDTH - 200, 100))
        
        # Draw stratagem cooldowns
        y_offset = 160
        for stratagem, cooldown in player.stratagem_cooldowns.items():
            if cooldown > 0:
                cooldown_text = self.font_small.render(
                    f"{stratagem.upper()}: {cooldown:.1f}s", True, ORANGE)
                screen.blit(cooldown_text, (20, y_offset))
                y_offset += 20
        
        # Draw limb status
        status_y = SCREEN_HEIGHT - 80
        if player.leg_injured:
            leg_text = self.font_small.render("LEG INJURED - MOVEMENT REDUCED", True, RED)
            screen.blit(leg_text, (20, status_y))
        if player.arm_injured:
            arm_text = self.font_small.render("ARM INJURED - ACCURACY REDUCED", True, RED)
            screen.blit(arm_text, (20, status_y + 20))
    
    def draw_game_over(self, screen, score, wave):
        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.font_huge.render("YOU DIED", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
        screen.blit(game_over_text, text_rect)
        
        # Score
        score_text = self.font_large.render(f"SCORE: {score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(score_text, score_rect)
        
        # Wave reached
        wave_text = self.font_medium.render(f"WAVES SURVIVED: {wave}", True, WHITE)
        wave_rect = wave_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        screen.blit(wave_text, wave_rect)
        
        # Restart prompt
        restart_text = self.font_medium.render("PRESS R TO RESTART", True, YELLOW)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 150))
        screen.blit(restart_text, restart_rect)
        
        # Democracy message
        demo_text = self.font_small.render("DEMOCRACY WILL REMEMBER YOUR SACRIFICE", 
                                           True, WHITE)
        demo_rect = demo_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 200))
        screen.blit(demo_text, demo_rect)
    
    def draw_stratagem_menu(self, screen, stratagem_system):
        stratagem_system.draw(screen)