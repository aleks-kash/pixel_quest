import pygame
import time
from src.constants import WIDTH, HEIGHT

class WriteLog:
    active_alerts = []
    is_paused = False

    @staticmethod
    def pause():
        WriteLog.is_paused = True

    @staticmethod
    def resume():
        WriteLog.is_paused = False

    def __init__(self, data, duration=100000):
        """
        Creates a new alert. 
        data: string or list of strings.
        duration: how long the alert stays on screen in milliseconds.
        """
        if isinstance(data, (list, tuple)):
            self.lines = [str(item) for item in data]
        else:
            self.lines = [str(data)]
        
        self.start_time = time.time() * 1000
        self.duration = duration
        self.fade_duration = 500  # ms for fade out
        
        # Add to static list for global tracking
        WriteLog.active_alerts.append(self)

    @staticmethod
    def update():
        now = time.time() * 1000
        # Remove expired alerts
        WriteLog.active_alerts = [a for a in WriteLog.active_alerts if now < a.start_time + a.duration + a.fade_duration]

    @staticmethod
    def draw(screen):
        if not WriteLog.active_alerts:
            return

        now = time.time() * 1000
        font = pygame.font.SysFont(None, 24)
        padding = 10
        margin = 10
        current_y = margin

        for alert in WriteLog.active_alerts:
            elapsed = now - alert.start_time
            alpha = 255
            
            # Fade out calculation
            if elapsed > alert.duration:
                fade_elapsed = elapsed - alert.duration
                alpha = max(0, 255 - int((fade_elapsed / alert.fade_duration) * 255))

            # Calculate rect size
            max_w = 0
            line_surfs = []
            for line in alert.lines:
                s = font.render(line, True, (255, 255, 255))
                line_surfs.append(s)
                max_w = max(max_w, s.get_width())

            total_h = len(line_surfs) * 25 + padding * 2
            total_w = max_w + padding * 2

            # Create surface for semi-transparent background
            bg_surf = pygame.Surface((total_w, total_h), pygame.SRCALPHA)
            pygame.draw.rect(bg_surf, (0, 0, 0, int(150 * (alpha / 255))), (0, 0, total_w, total_h), border_radius=5)
            
            # Blit text to bg_surf with alpha
            y_offset = padding
            for s in line_surfs:
                if alpha < 255:
                    s.set_alpha(alpha)
                bg_surf.blit(s, (padding, y_offset))
                y_offset += 25

            # Position in top-right or stack vertically
            screen.blit(bg_surf, (WIDTH - total_w - margin, current_y))
            current_y += total_h + margin
