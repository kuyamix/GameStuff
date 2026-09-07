import pygame
from config import *
from utils import world_to_screen, is_unlocked

class UI:
    def __init__(self, game):
        self.game = game
        self.ui_scale = min(SCREEN_WIDTH / 940, SCREEN_HEIGHT / 2030)
        self.update_rects()
        self.fonts = self.create_fonts()
    
    def update_rects(self):
        s = self.ui_scale
        bs, bm = int(80*s), int(20*s)
        bx = SCREEN_WIDTH - bs - bm
        by = SCREEN_HEIGHT - bs*3 - 10*s*2 - bm
        
        self.strafe_btn = pygame.Rect(bx, by, bs, bs)
        self.mortar_btn = pygame.Rect(bx, by + bs + 10*s, bs, bs)
        self.mrls_btn = pygame.Rect(bx, by + bs*2 + 20*s, bs, bs)
        self.upgrade_btn = pygame.Rect(SCREEN_WIDTH//2 - 80*s, SCREEN_HEIGHT - 80*s, 160*s, 50*s)
        self.cancel_btn = pygame.Rect(SCREEN_WIDTH//2 - 50*s, SCREEN_HEIGHT - 50*s, 100*s, 40*s)
        self.zoom_in = pygame.Rect(SCREEN_WIDTH - 45*s - 10*s, 120*s, 45*s, 45*s)
        self.zoom_out = pygame.Rect(SCREEN_WIDTH - 45*s - 10*s, 170*s, 45*s, 45*s)
        self.minimap = pygame.Rect(15*s, SCREEN_HEIGHT - 120*s - 15*s, 120*s, 120*s)
    
    def create_fonts(self):
        s = self.ui_scale
        fs = max(14, int(20*s))
        return {
            'small': pygame.font.Font(None, fs),
            'medium': pygame.font.Font(None, int(fs * 1.3)),
            'big': pygame.font.Font(None, int(fs * 2)),
            'huge': pygame.font.Font(None, int(fs * 3))
        }
    
    def draw(self, screen):
        if self.game.aiming_mode:
            self.draw_aiming(screen)
            return
        
        # Health
        bw, bh = int(200*self.ui_scale), int(20*self.ui_scale)
        pygame.draw.rect(screen, RED, (15*self.ui_scale, 15*self.ui_scale, bw, bh))
        ratio = self.game.player_health / self.game.player_max_health
        pygame.draw.rect(screen, GREEN, (15*self.ui_scale, 15*self.ui_scale, bw * ratio, bh))
        screen.blit(self.fonts['small'].render(f"HP: {int(self.game.player_health)}/{int(self.game.player_max_health)}", True, WHITE), (20*self.ui_scale, 17*self.ui_scale))
        
        # XP
        bw, bh = int(200*self.ui_scale), int(16*self.ui_scale)
        pygame.draw.rect(screen, (30,30,50), (15*self.ui_scale, 40*self.ui_scale, bw, bh))
        ratio = self.game.xp / self.game.xp_to_next if self.game.xp_to_next > 0 else 0
        pygame.draw.rect(screen, BLUE, (15*self.ui_scale, 40*self.ui_scale, bw * ratio, bh))
        screen.blit(self.fonts['small'].render(f"XP: {int(self.game.xp)}/{int(self.game.xp_to_next)}", True, WHITE), (20*self.ui_scale, 42*self.ui_scale))
        
        # Info
        t = self.game.game_time // 60
        screen.blit(self.fonts['small'].render(f"Level {self.game.level}  Kills: {self.game.enemies_killed}  Time: {t}s", True, WHITE), (230*self.ui_scale, 15*self.ui_scale))
        screen.blit(self.fonts['small'].render(f"Enemies: {len(self.game.enemies)}/60", True, WHITE), (230*self.ui_scale, 35*self.ui_scale))
        
        # Ability status
        y = 15*self.ui_scale
        for ability, label in [('strafe', '✈️'), ('mortar', '💥'), ('mrls', '🚀')]:
            if is_unlocked(self.game.level, ability):
                cd = getattr(self.game, f'{ability}_cooldown')
                status = "READY" if cd == 0 else f"{cd//60+1}s"
                color = GREEN if cd == 0 else GRAY
                text = self.fonts['small'].render(f"{label} {status}", True, color)
                screen.blit(text, (SCREEN_WIDTH - text.get_width() - 15*self.ui_scale, y))
                y += 22*self.ui_scale
        
        # Buttons
        self.draw_ability_buttons(screen)
        self.draw_minimap(screen)
        self.draw_zoom(screen)
        
        # Help text
        help_text = self.fonts['small'].render("WASD: Move | 1:Strafe 2:Mortar 3:MRLS | ESC:Cancel | R:Restart", True, (150,150,150))
        screen.blit(help_text, (SCREEN_WIDTH//2 - help_text.get_width()//2, SCREEN_HEIGHT - 30))
        
        # Upgrade
        if self.game.xp >= self.game.xp_to_next:
            pygame.draw.rect(screen, YELLOW, self.upgrade_btn, border_radius=12)
            pygame.draw.rect(screen, WHITE, self.upgrade_btn, 3, border_radius=12)
            screen.blit(self.fonts['medium'].render("⬆ UPGRADE", True, BLACK), 
                       (self.upgrade_btn.x + 20*self.ui_scale, self.upgrade_btn.y + 12*self.ui_scale))
    
    def draw_ability_buttons(self, screen):
        buttons = [
            ('strafe', self.strafe_btn, '✈️', 'STRAFE', (200,150,50)),
            ('mortar', self.mortar_btn, '💥', 'MORTAR', (200,80,50)),
            ('mrls', self.mrls_btn, '🚀', 'MRLS', (200,100,50))
        ]
        for ability, rect, icon, label, color in buttons:
            unlocked = is_unlocked(self.game.level, ability)
            cd = getattr(self.game, f'{ability}_cooldown')
            color = GRAY if (cd > 0 or not unlocked) else color
            pygame.draw.rect(screen, color, rect, border_radius=12)
            pygame.draw.rect(screen, WHITE, rect, 3, border_radius=12)
            screen.blit(self.fonts['medium'].render(icon if unlocked else "🔒", True, WHITE), (rect.x + 15, rect.y + 10))
            screen.blit(self.fonts['small'].render(label, True, WHITE), (rect.x + (8 if ability!='mortar' else 5), rect.y + 55))
            if cd > 0 and unlocked:
                ratio = cd / getattr(self, f'{ability}_max_cooldown', 300)
                pygame.draw.rect(screen, (0,0,0,150), (rect.x, rect.y, rect.width, rect.height * ratio))
                screen.blit(self.fonts['small'].render(f"{cd//60+1}s", True, WHITE), (rect.x + 28, rect.y + 30))
            elif not unlocked:
                screen.blit(self.fonts['small'].render(f"Lv{UNLOCK_LEVELS[ability]}", True, WHITE), (rect.x + 20, rect.y + 30))
    
    def draw_minimap(self, screen):
        pygame.draw.rect(screen, (20,20,30), self.minimap)
        pygame.draw.rect(screen, (80,80,120), self.minimap, 2)
        sx, sy = self.minimap.width / MAP_WIDTH, self.minimap.height / MAP_HEIGHT
        
        for enemy in self.game.enemies:
            mx, my = self.minimap.x + enemy.x * sx, self.minimap.y + enemy.y * sy
            color = (255,0,0) if enemy.type in ['leviathan','titan','colossus'] else (200,100,0) if enemy.type in ['behemoth','juggernaut'] else RED
            pygame.draw.circle(screen, color, (int(mx), int(my)), 3 if enemy.type in ['leviathan','titan','colossus'] else 2)
        
        for gem in self.game.gems:
            mx, my = self.minimap.x + gem.x * sx, self.minimap.y + gem.y * sy
            pygame.draw.circle(screen, YELLOW, (int(mx), int(my)), 1)
        
        px, py = self.minimap.x + self.game.player_x * sx, self.minimap.y + self.game.player_y * sy
        pygame.draw.circle(screen, GREEN, (int(px), int(py)), 4)
        
        # Viewport
        vx = (self.game.camera_x - SCREEN_WIDTH/2/self.game.zoom_level) * sx + self.minimap.x
        vy = (self.game.camera_y - SCREEN_HEIGHT/2/self.game.zoom_level) * sy + self.minimap.y
        vw, vh = (SCREEN_WIDTH/self.game.zoom_level) * sx, (SCREEN_HEIGHT/self.game.zoom_level) * sy
        pygame.draw.rect(screen, WHITE, (vx, vy, vw, vh), 1)
    
    def draw_zoom(self, screen):
        for btn, label in [(self.zoom_in, '+'), (self.zoom_out, '-')]:
            pygame.draw.rect(screen, DARK_GRAY, btn, border_radius=10)
            pygame.draw.rect(screen, WHITE, btn, 2, border_radius=10)
            screen.blit(self.fonts['big'].render(label, True, WHITE), (btn.x + 14, btn.y + 5))
        screen.blit(self.fonts['small'].render(f"{int(self.game.zoom_level*100)}%", True, WHITE), (SCREEN_WIDTH - 70, 240))
    
    def draw_aiming(self, screen):
        sx, sy = world_to_screen(self.game.aim_x, self.game.aim_y, self.game.camera_x, self.game.camera_y, self.game.zoom_level)
        # Reticle
        pygame.draw.circle(screen, WHITE, (int(sx), int(sy)), 40, 3)
        pygame.draw.circle(screen, RED, (int(sx), int(sy)), 40, 2)
        for dx, dy in [(-60,0), (20,0), (0,-60), (0,20)]:
            pygame.draw.line(screen, WHITE, (sx+dx, sy+dy), (sx+dx+40, sy+dy), 3) if dx != 0 else pygame.draw.line(screen, WHITE, (sx+dx, sy+dy), (sx+dx, sy+dy+40), 3)
        pygame.draw.circle(screen, RED, (int(sx), int(sy)), 5)
        
        # Label
        labels = {'strafe': ('✈️ STRAFE', YELLOW), 'mortar': ('💥 MORTAR', ORANGE), 'mrls': ('🚀 MRLS', CYAN)}
        if self.game.aiming_ability in labels:
            text, color = labels[self.game.aiming_ability]
            screen.blit(self.fonts['medium'].render(text, True, color), (sx - 50, sy - 90))
        
        # Cancel
        pygame.draw.rect(screen, RED, self.cancel_btn, border_radius=8)
        pygame.draw.rect(screen, WHITE, self.cancel_btn, 2, border_radius=8)
        screen.blit(self.fonts['medium'].render("CANCEL", True, WHITE), (self.cancel_btn.x + 12, self.cancel_btn.y + 8))
        screen.blit(self.fonts['small'].render("Click to aim | Right-click to cancel", True, WHITE), (SCREEN_WIDTH//2 - 150, 10))
    
    def draw_notifications(self, screen):
        y = 0
        for notif in self.game.level_up_notifications[:]:
            alpha = min(1.0, notif['timer'] / 30)
            text = self.fonts['huge'].render(notif['text'], True, YELLOW)
            text.set_alpha(int(255 * alpha))
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 100 + y))
            sub = self.fonts['medium'].render(notif['subtext'], True, WHITE)
            sub.set_alpha(int(200 * alpha))
            screen.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, 160 + y))
            notif['timer'] -= 1
            if notif['timer'] <= 0:
                self.game.level_up_notifications.remove(notif)
            y += 80