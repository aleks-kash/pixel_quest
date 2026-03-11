import pygame

from src.constants import *
from src.player.player import Player

class Camera:
    camera_x = 0
    camera_y = 0
    zoom = 1.0
    zoom_enabled = True 
    logical_w = int(WIDTH)
    logical_h = int(HEIGHT)
    follow_player = True

    @classmethod
    def init(cls):
        cls.camera_x = 0
        cls.camera_y = 0
        cls.zoom_enabled = True
        cls.zoom = 1.0
        cls.logical_w = int(WIDTH / cls.zoom)
        cls.logical_h = int(HEIGHT / cls.zoom)

    # Camera Follow
    @classmethod
    def follow(cls, level: int, player: Player):
        if level == 0:
            cls.camera_x = 0
            cls.camera_y = 0
        else:
            cls.camera_x = player.rect.centerx - cls.logical_w // 2
            if cls.camera_x < 0: cls.camera_x = 0
            
            # Use original locked vertical camera if zoom is 1.0
            if cls.zoom == 1.0:
                cls.camera_y = 0
            else:
                cls.camera_y = player.rect.centery - cls.logical_h // 2

    # def update(self, target):
    #     if self.follow_player:
    #         self.camera_x = target.rect.centerx - self.logical_w // 2
    #         self.camera_y = target.rect.centery - self.logical_h // 2

    # def apply(self, rect):
    #     return rect.move(int(-self.x), int(-self.y))


    @classmethod
    def update_logical(cls):
        cls.logical_w = int(WIDTH / cls.zoom)
        cls.logical_h = int(HEIGHT / cls.zoom)

    @classmethod
    def zoom_update(cls, state: str, key: pygame.key.ScancodeWrapper):
        if state == 'playing':

            if key == pygame.K_p:
                cls.zoom_toggle()
                if not cls.zoom_enabled:
                    cls.zoom_default()

            if cls.zoom_enabled and key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                cls.zoom_in()
            elif cls.zoom_enabled and key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                cls.zoom_out()

    @classmethod
    def zoom_default(cls):
        cls.zoom = 1.0
        cls.update_logical()

    @classmethod
    def zoom_toggle(cls):
        cls.zoom_enabled = not cls.zoom_enabled

    # Zoom in (closer to original 1.0)
    @classmethod
    def zoom_in(cls):
        if cls.zoom == 0.25:
            cls.zoom = 0.5
        elif cls.zoom == 0.5:
            cls.zoom = 1.0
        cls.update_logical()

    # Zoom out
    @classmethod
    def zoom_out(cls):
        if cls.zoom == 1.0:
            cls.zoom = 0.5
        elif cls.zoom == 0.5:
            cls.zoom = 0.25
        cls.update_logical()

    # def draw_red_frame(self, screen, target_rect, level):
    #     if self.zoom_enabled and self.zoom != 1.0:
    #         old_cam_x = 0 if level == 0 else max(0, target_rect.centerx - self.width // 2)
    #         old_cam_y = 0
    #         red_rect_x = old_cam_x - self.x
    #         red_rect_y = old_cam_y - self.y
            
    #         red_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
    #         red_surf.fill((255, 0, 0, 50))
    #         pygame.draw.rect(red_surf, (255, 0, 0, 255), red_surf.get_rect(), 4)
    #         screen.blit(red_surf, (red_rect_x, red_rect_y))

    @classmethod
    def draw_red_frame(cls, screen, player, level):
        # --- DRAW RED FRAME (Old View) ---
        if getattr(cls, "zoom_enabled", True) and getattr(cls, "zoom", 1.0) != 1.0:
            old_cam_x = 0 if level == 0 else max(0, player.rect.centerx - WIDTH // 2)
            old_cam_y = 0
            red_rect_x = old_cam_x - cls.camera_x
            red_rect_y = old_cam_y - cls.camera_y
            
            red_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            red_surf.fill((255, 0, 0, 50))
            pygame.draw.rect(red_surf, (255, 0, 0, 255), red_surf.get_rect(), 4)
            screen.blit(red_surf, (red_rect_x, red_rect_y))