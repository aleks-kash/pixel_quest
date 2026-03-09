import pygame
import sys
import math
import time

from src.constants import *

from src.player.player import Player
from src.platform.platform_obj import Platform
from src.item.item import Item
from src.npc.npc import NPC
from src.projectile.projectile import Projectile
from src.npc.enemy.red_patrol_unit import RedPatrolUnit

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pixel Quest Python")
        self.clock = pygame.time.Clock()
        self.player = Player()
        #self.camera = Camera()
        self.camera_x = 0
        self.camera_y = 0
        self.zoom_enabled = True
        self.zoom = 1.0
        self.logical_w = int(WIDTH / self.zoom)
        self.logical_h = int(HEIGHT / self.zoom)
        self.level = 0
        self.next_level = 1
        self.state = 'menu'
        self.load_level(0)

    def load_level(self, lvl):
        self.level = lvl
        self.projectiles = []
        self.items = []
        self.platforms = []
        self.npcs = []

        if lvl == 0:
            self.platforms = [
                Platform(0, 0, 30, 450, (69, 26, 3), 'solid'),
                Platform(770, 0, 30, 450, (69, 26, 3), 'solid'),
                Platform(0, 400, 800, 50, (120, 53, 15), 'solid'),
                Platform(0, 0, 800, 50, (69, 26, 3), 'solid'),
                Platform(640, 260, 40, 120, (0,0,0), 'goal'), # Portal
                Platform(600, 380, 120, 20, (69, 26, 3), 'solid'),
            ]
            self.npcs = [
                NPC(400, 360, 32, 40, (139, 92, 246), 0, 'friendly', 0, 1)
            ]
        elif lvl == 1:
            self.platforms = [
                Platform(0, 400, 600, 50, PLATFORM_COLOR, 'solid'),
                Platform(700, 400, 600, 50, PLATFORM_COLOR, 'solid'),
                Platform(600, 320, 100, 20, WOOD_COLOR, 'wood'),
                Platform(250, 300, 120, 20, WOOD_COLOR, 'wood'),
                Platform(450, 220, 120, 20, WOOD_COLOR, 'wood'),
                Platform(800, 300, 120, 20, WOOD_COLOR, 'wood'),
                Platform(1000, 220, 120, 20, WOOD_COLOR, 'wood'),
                Platform(1200, 150, 100, 20, GOAL_COLOR, 'goal'),
                Platform(600, 420, 100, 30, LAVA_COLOR, 'lava'),
            ]
            for cx, cy in [(300, 260), (500, 180), (650, 280), (850, 260), (1050, 180)]:
                self.items.append(Item(cx, cy, 'coin'))
            self.items.append(Item(1100, 110, 'heart'))
            
            self.npcs = [
                RedPatrolUnit(400, 368, 2, 150),
                RedPatrolUnit(900, 368, -2, 150),
                NPC(100, 368, 32, 40, (139, 92, 246), 0, 'friendly', 0, 1),
            ]
        elif lvl == 2:
            self.platforms = [
                Platform(0, 400, 400, 50, PLATFORM_COLOR, 'solid'),
                Platform(500, 400, 400, 50, PLATFORM_COLOR, 'solid'),
                Platform(1000, 400, 400, 50, PLATFORM_COLOR, 'solid'),
                Platform(400, 320, 100, 20, WOOD_COLOR, 'wood'),
                Platform(900, 320, 100, 20, WOOD_COLOR, 'wood'),
                Platform(200, 250, 150, 20, WOOD_COLOR, 'wood'),
                Platform(600, 200, 150, 20, WOOD_COLOR, 'wood'),
                Platform(950, 250, 150, 20, WOOD_COLOR, 'wood'),
                Platform(1250, 200, 100, 20, WOOD_COLOR, 'wood'),
                Platform(1450, 150, 100, 20, GOAL_COLOR, 'goal'),
                Platform(400, 420, 100, 30, LAVA_COLOR, 'lava'),
                Platform(900, 420, 100, 30, LAVA_COLOR, 'lava'),
            ]
            for cx, cy in [(250, 210), (650, 160), (1150, 210)]:
                self.items.append(Item(cx, cy, 'coin'))
            self.items.append(Item(1300, 110, 'heart'))
            
            self.npcs = [
                NPC(300, 368, 32, 32, GINGERBREAD_COLOR, 1, 'gingerbread', 100, 2),
                NPC(700, 368, 32, 32, GINGERBREAD_COLOR, -1, 'gingerbread', 100, 2),
                NPC(1200, 368, 32, 32, GINGERBREAD_COLOR, 1, 'gingerbread', 100, 2),
                NPC(950, 218, 32, 32, ENEMY_COLOR, 1.5, 'enemy', 60, 1),
            ]

    def handle_damage(self):
        now = time.time() * 1000
        if now < self.player.invulnerable_until:
            return
        self.player.health -= 1
        self.player.invulnerable_until = now + 1500
        self.player.vx = -10 if self.player.direction == 'right' else 10
        self.player.vy = -4
        self.player.knockback = 15
        if self.player.health <= 0:
            self.state = 'gameOver'

    def update(self):
        if self.state != 'playing':
            return

        keys = pygame.key.get_pressed()
        res = self.player.update(keys, self.platforms)
        
        # Hub bounds
        if self.level == 0:
            if self.player.rect.left < 30:
                self.player.rect.left = 30
                self.player.x = float(self.player.rect.x)
                self.player.vx = 0
            if self.player.rect.right > 770:
                self.player.rect.right = 770
                self.player.x = float(self.player.rect.x)
                self.player.vx = 0
        
        if res == "goal":
            if self.level == 0:
                self.load_level(self.next_level)
                self.player.reset(50, 300, self.player.score, self.player.health)
            elif self.level == 1:
                self.next_level = 2
                self.load_level(0)
                self.player.reset(80, 350, self.player.score, self.player.health)
            else:
                self.state = 'win'
        elif res == "lava":
            self.state = 'gameOver'

        # Items
        for item in self.items:
            if not item.collected and self.player.rect.colliderect(item.rect):
                item.collected = True
                if item.type == 'coin':
                    self.player.score += 10
                elif item.type == 'heart':
                    self.player.health += 1

        # NPCs
        now = time.time() * 1000
        for npc in self.npcs:
            if npc.health <= 0: continue
            
            if npc.type in ['enemy', 'gingerbread']:
                npc.rect.x += npc.vx
                if abs(npc.rect.x - npc.start_x) > npc.patrol_range:
                    npc.vx *= -1

                if npc.type == 'gingerbread' and now - npc.last_shoot_time > npc.shoot_cooldown:
                    dir = -1 if self.player.rect.x < npc.rect.x else 1
                    px = npc.rect.right if dir == 1 else npc.rect.left - 10
                    self.projectiles.append(Projectile(px, npc.rect.centery - 5, 10, 10, dir * 4, 'npc'))
                    npc.last_shoot_time = now

                if self.player.rect.colliderect(npc.rect):
                    if self.player.vy > 0 and self.player.rect.bottom - self.player.vy <= npc.rect.top + 15:
                        npc.health -= 1
                        self.player.vy = -8
                        if npc.health <= 0:
                            npc.rect.y = -1000
                            self.player.score += 50
                    else:
                        self.handle_damage()

        # Projectiles
        for p in self.projectiles[:]:
            p.rect.x += p.vx
            p.distance += abs(p.vx)
            if p.owner == 'npc' and p.rect.colliderect(self.player.rect):
                if now > self.player.invulnerable_until:
                    self.handle_damage()
                    self.player.vx = p.vx * 1.5
                    self.player.vy = -4
                    self.player.knockback = 15
                self.projectiles.remove(p)
            elif p.rect.x < self.camera_x - 100 or p.rect.x > self.camera_x + WIDTH + 100 or p.distance > p.max_distance:
                self.projectiles.remove(p)

        # Camera Follow
        if self.level == 0:
            self.camera_x = 0
            self.camera_y = 0
        else:
            self.camera_x = self.player.rect.centerx - self.logical_w // 2
            if self.camera_x < 0: self.camera_x = 0
            
            # Use original locked vertical camera if zoom is 1.0
            if self.zoom == 1.0:
                self.camera_y = 0
            else:
                self.camera_y = self.player.rect.centery - self.logical_h // 2

        # Bounds
        if self.player.rect.y > HEIGHT + 100:
            self.state = 'gameOver'

    def draw_bg(self, lvl, screen, cam_x):
        cam_y = self.camera_y
        h = HEIGHT - int(cam_y)
        if lvl == 1:
            screen.fill((224, 242, 254))
            for i in range(3):
                x = int((i * 500 - cam_x * 0.1) % (WIDTH + 500)) - 250
                pygame.draw.polygon(screen, (147, 197, 253), [(x, h), (x + 250, h - 150), (x + 500, h)])
            for i in range(4):
                x = int((i * 400 - cam_x * 0.3) % (WIDTH + 400)) - 200
                pygame.draw.polygon(screen, (96, 165, 250), [(x, h), (x + 200, h - 80), (x + 400, h)])
            for i in range(6):
                x = int((i * 350 - cam_x * 0.7) % (WIDTH + 350)) - 175
                pygame.draw.ellipse(screen, (52, 211, 153), (x, h - 5, 120, 60))
        elif lvl == 2:
            screen.fill((30, 27, 75))
            for i in range(3):
                x = int((i * 600 - cam_x * 0.1) % (WIDTH + 600)) - 300
                pygame.draw.polygon(screen, (49, 46, 129), [(x, h), (x + 300, h - 200), (x + 600, h)])
            for i in range(8):
                x = int((i * 200 - cam_x * 0.6) % (WIDTH + 200)) - 100
                pygame.draw.polygon(screen, (17, 24, 39), [(x, h), (x + 50, h - 120), (x + 100, h)])
            for i in range(50):
                x = (i * 12345) % WIDTH
                y = (i * 54321) % (HEIGHT - 100) - int(cam_y)
                sz = (i % 2) + 1
                pygame.draw.rect(screen, (255, 255, 255), (x, y, sz, sz))
            pygame.draw.circle(screen, (253, 230, 138), (WIDTH - 80, 60 - int(cam_y)), 30)

    def draw(self):
        real_screen = self.screen
        self.screen = pygame.Surface((self.logical_w, self.logical_h))

        if self.level == 0:
            self.screen.fill((120, 53, 15))
            pygame.draw.rect(self.screen, (255, 255, 255), (325 - self.camera_x, 150 - self.camera_y, 150, 150), 6)
            old_clip = self.screen.get_clip()
            self.screen.set_clip(pygame.Rect(325 - self.camera_x, 150 - self.camera_y, 150, 150))
            self.draw_bg(self.next_level, self.screen, 0)
            self.screen.set_clip(old_clip)
            
            px, py = 640 - self.camera_x, 260 - self.camera_y
            pygame.draw.circle(self.screen, (249, 115, 22), (px + 20, py + 20), 22)
            pygame.draw.circle(self.screen, (251, 146, 60), (px + 20, py + 20), 10)
            
            pygame.draw.rect(self.screen, (153, 27, 27), (200 - self.camera_x, 380 - self.camera_y, 400, 20))
            pygame.draw.rect(self.screen, GOAL_COLOR, (60 - self.camera_x, 320 - self.camera_y, 80, 80))
        else:
            self.draw_bg(self.level, self.screen, self.camera_x)
        
        for p in self.platforms:
            color = LAVA_COLOR if p.type == 'lava' else p.color
            if p.type != 'goal' or self.level != 0:
                pygame.draw.rect(self.screen, color, (p.rect.x - self.camera_x, p.rect.y - self.camera_y, p.rect.width, p.rect.height))

        for i in self.items:
            if not i.collected:
                if i.type == 'coin':
                    pygame.draw.circle(self.screen, COIN_COLOR, (i.rect.centerx - self.camera_x, i.rect.centery - self.camera_y), i.rect.width // 2)
                else:
                    pygame.draw.rect(self.screen, HEART_COLOR, (i.rect.x - self.camera_x, i.rect.y - self.camera_y, i.rect.width, i.rect.height))

        for n in self.npcs:
            if n.health <= 0: continue
            nx = n.rect.x - self.camera_x
            ny = n.rect.y - self.camera_y
            if n.type == 'gingerbread':
                pygame.draw.ellipse(self.screen, n.color, (nx, ny, n.rect.width, n.rect.height))
                pygame.draw.rect(self.screen, (33,33,33), (nx, ny - 10, n.rect.width, 4))
                pygame.draw.rect(self.screen, (239, 68, 68), (nx, ny - 10, int(n.rect.width * (n.health / n.max_health)), 4))
            else:
                pygame.draw.rect(self.screen, n.color, (nx, ny, n.rect.width, n.rect.height))
                pygame.draw.rect(self.screen, (255, 255, 255), (nx + 5, ny + 5, 6, 6))

        for p in self.projectiles:
            if p.owner == 'npc':
                pygame.draw.circle(self.screen, (217, 119, 6), (p.rect.centerx - self.camera_x, p.rect.centery - self.camera_y), p.rect.width // 2)

        now = time.time() * 1000
        is_visible = now >= self.player.invulnerable_until or int(now / 150) % 2 == 0
        if is_visible:
            px = self.player.rect.x - self.camera_x
            py = self.player.rect.y - self.camera_y
            pygame.draw.rect(self.screen, PLAYER_COLOR, (px, py, self.player.rect.width, self.player.rect.height))
            pygame.draw.rect(self.screen, (255, 255, 255), (px + (18 if self.player.direction == 'right' else 5), py + 10, 8, 8))

        # --- DRAW RED FRAME (Old View) ---
        if getattr(self, "zoom_enabled", True) and getattr(self, "zoom", 1.0) != 1.0:
            old_cam_x = 0 if self.level == 0 else max(0, self.player.rect.centerx - WIDTH // 2)
            old_cam_y = 0
            red_rect_x = old_cam_x - self.camera_x
            red_rect_y = old_cam_y - self.camera_y
            
            red_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            red_surf.fill((255, 0, 0, 50))
            pygame.draw.rect(red_surf, (255, 0, 0, 255), red_surf.get_rect(), 4)
            self.screen.blit(red_surf, (red_rect_x, red_rect_y))

        # Scale and blit virtual surface to real screen
        scaled_surf = pygame.transform.scale(self.screen, (WIDTH, HEIGHT))
        self.screen = real_screen
        self.screen.blit(scaled_surf, (0, 0))

        font = pygame.font.SysFont(None, 36)
        self.screen.blit(font.render(f"Hearts: {self.player.health}", True, (0, 0, 0)), (20, 20))
        self.screen.blit(font.render(f"Score: {self.player.score}", True, (0, 0, 0)), (150, 20))
        lvl_str = "Home" if self.level == 0 else str(self.level)
        self.screen.blit(font.render(f"Level: {lvl_str}", True, (0, 0, 0)), (300, 20))

        if self.state in ['menu', 'gameOver', 'win']:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            txt1 = "PIXEL QUEST" if self.state == 'menu' else ("GAME OVER" if self.state == 'gameOver' else "YOU WIN!")
            txt2 = "Press SPACE to start" if self.state == 'menu' else "Press R to retry"
            self.screen.blit(pygame.font.SysFont(None, 72).render(txt1, True, (255, 255, 255)), (WIDTH // 2 - 150, HEIGHT // 2 - 50))
            self.screen.blit(pygame.font.SysFont(None, 36).render(txt2, True, (200, 200, 200)), (WIDTH // 2 - 100, HEIGHT // 2 + 20))

        pygame.display.flip()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if self.state == 'menu' and event.key == pygame.K_SPACE:
                        self.state = 'playing'
                        self.load_level(1)
                        self.player.reset(50, 300)
                    if self.state in ['gameOver', 'win'] and event.key == pygame.K_r:
                        if self.state == 'gameOver':
                            self.load_level(self.level)
                            self.player.reset(50, 300, self.player.score, 3)
                        else:
                            self.level = 1
                            self.next_level = 2
                            self.load_level(1)
                            self.player.reset(50, 300)
                        self.state = 'playing'
                    
                    if self.state == 'playing':
                        if event.key == pygame.K_p:
                            self.zoom_enabled = not getattr(self, "zoom_enabled", True)
                            if not self.zoom_enabled:
                                self.zoom = 1.0
                                self.logical_w = int(WIDTH / self.zoom)
                                self.logical_h = int(HEIGHT / self.zoom)

                        if getattr(self, "zoom_enabled", True):
                            if event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                                # Zoom in (closer to original 1.0)
                                if self.zoom == 0.25: self.zoom = 0.5
                                elif self.zoom == 0.5: self.zoom = 1.0
                                self.logical_w = int(WIDTH / self.zoom)
                                self.logical_h = int(HEIGHT / self.zoom)
                            elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                                # Zoom out
                                if self.zoom == 1.0: self.zoom = 0.5
                                elif self.zoom == 0.5: self.zoom = 0.25
                                self.logical_w = int(WIDTH / self.zoom)
                                self.logical_h = int(HEIGHT / self.zoom)
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Game().run()
