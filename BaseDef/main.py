import pygame
import sys
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from systems.game import Game

def main():
    pygame.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Base Defense | Command Center")
    clock = pygame.time.Clock()
    
    # Fonts
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    large_font = pygame.font.Font(None, 72)
    title_font = pygame.font.Font(None, 42)
    ui_font = pygame.font.Font(None, 28)
    small_bold_font = pygame.font.Font(None, 22)
    
    game = Game(screen, font, small_font, large_font, title_font, ui_font, small_bold_font)
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    game.start_wave()
                elif event.key == pygame.K_1:
                    game.placing_tower = not game.placing_tower
                    if game.placing_tower:
                        game.artillery_mode = False
                        game.strafe_mode = False
                elif event.key == pygame.K_2:
                    game.artillery_mode = not game.artillery_mode
                    if game.artillery_mode:
                        game.placing_tower = False
                        game.strafe_mode = False
                elif event.key == pygame.K_3:
                    game.strafe_mode = not game.strafe_mode
                    if game.strafe_mode:
                        game.placing_tower = False
                        game.artillery_mode = False
                elif event.key == pygame.K_r and game.game_over:
                    game = Game(screen, font, small_font, large_font, title_font, ui_font, small_bold_font)
                elif event.key == pygame.K_c:
                    game.camera.center_on(game.base.rect.centerx, game.base.rect.centery)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not game.game_over:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    world_x, world_y = game.camera.screen_to_world(mouse_x, mouse_y)
                    if game.artillery_mode:
                        game.call_artillery(world_x, world_y)
                    elif game.strafe_mode:
                        game.call_strafing_run(world_x, world_y)
                    elif game.placing_tower:
                        game.place_tower(world_x, world_y)
                elif event.button == 4:
                    game.camera.apply_zoom(0.1)
                elif event.button == 5:
                    game.camera.apply_zoom(-0.1)
            elif event.type == pygame.MOUSEMOTION:
                game.tower_preview_pos = pygame.mouse.get_pos()
        
        game.update()
        game.draw()
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()