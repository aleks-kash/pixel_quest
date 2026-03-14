import pygame
import sys
import math
import time

from src.constants import *
from src.control.camera import Camera
from src.player.player import Player
from src.platform.platform_obj import Platform
from src.item.item import Item
from src.level.level import Level
from src.npc.npc import NPC
from src.projectile.projectile import Projectile
from src.npc.enemy.red_patrol_unit import RedPatrolUnit
from src.control.write_log import WriteLog


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Pixel Quest Python")
        self.clock = pygame.time.Clock()
        self.player = Player()
        self.k_level = 0
        self.next_level = 1
        self.state = 'menu'
        self.load_level(0)

    def load_level(self, lvl):
        self.k_level = lvl
        self.projectiles = []
        self.items = []
        self.platforms = []
        self.npcs = []

        self.level = Level(lvl)

        self.platforms = self.level.get_platforms()
        self.projectiles = self.level.get_projectiles()
        self.items = self.level.get_items()
        self.npcs = self.level.get_npcs()

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
        if self.state != 'playing' or WriteLog.is_paused:
            return

        keys = pygame.key.get_pressed()
        res = self.player.update(keys, self.platforms)
        
        # Hub bounds
        if self.k_level == 0:
            if self.player.rect.left < 30:
                self.player.rect.left = 30
                self.player.x = float(self.player.rect.x)
                self.player.vx = 0
            if self.player.rect.right > 770:
                self.player.rect.right = 770
                self.player.x = float(self.player.rect.x)
                self.player.vx = 0
        
        if res == "goal":
            if self.k_level == 0:
                self.load_level(self.next_level)
                self.player.reset(50, 300, self.player.score, self.player.health)
            elif self.k_level == 1:
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
            elif p.rect.x < Camera.camera_x - 100 or p.rect.x > Camera.camera_x + WIDTH + 100 or p.distance > p.max_distance:
                self.projectiles.remove(p)

        # Camera Follow
        Camera.follow(self.k_level, self.player)

        # Bounds
        if self.player.rect.y > HEIGHT + 100:
            self.state = 'gameOver'

        WriteLog.update()


    def draw_bg(self, lvl, screen, cam_x):
        if lvl == 1:
            Level(1).draw_background(screen, cam_x)
        elif lvl == 2:
            Level(2).draw_background(screen, cam_x)

    def draw(self):
        real_screen = self.screen
        self.screen = pygame.Surface((Camera.logical_w, Camera.logical_h))

        if self.k_level == 0:
            self.screen.fill((120, 53, 15))
            pygame.draw.rect(self.screen, (255, 255, 255), (325 - Camera.camera_x, 150 - Camera.camera_y, 150, 150), 6)
            old_clip = self.screen.get_clip()
            self.screen.set_clip(pygame.Rect(325 - Camera.camera_x, 150 - Camera.camera_y, 150, 150))
            self.draw_bg(self.next_level, self.screen, 0)
            self.screen.set_clip(old_clip)
            
            px, py = 640 - Camera.camera_x, 260 - Camera.camera_y
            pygame.draw.circle(self.screen, (249, 115, 22), (px + 20, py + 20), 22)
            pygame.draw.circle(self.screen, (251, 146, 60), (px + 20, py + 20), 10)
            
            pygame.draw.rect(self.screen, (153, 27, 27), (200 - Camera.camera_x, 380 - Camera.camera_y, 400, 20))
            pygame.draw.rect(self.screen, GOAL_COLOR, (60 - Camera.camera_x, 320 - Camera.camera_y, 80, 80))
        else:
            self.draw_bg(self.k_level, self.screen, Camera.camera_x)
        
        for p in self.platforms:
            color = LAVA_COLOR if p.type == 'lava' else p.color
            if p.type != 'goal' or self.k_level != 0:
                pygame.draw.rect(self.screen, color, (p.rect.x - Camera.camera_x, p.rect.y - Camera.camera_y, p.rect.width, p.rect.height))

        for i in self.items:
            if not i.collected:
                if i.type == 'coin':
                    pygame.draw.circle(self.screen, COIN_COLOR, (i.rect.centerx - Camera.camera_x, i.rect.centery - Camera.camera_y), i.rect.width // 2)
                else:
                    pygame.draw.rect(self.screen, HEART_COLOR, (i.rect.x - Camera.camera_x, i.rect.y - Camera.camera_y, i.rect.width, i.rect.height))

        for n in self.npcs:
            if n.health <= 0: continue
            nx = n.rect.x - Camera.camera_x
            ny = n.rect.y - Camera.camera_y
            if n.type == 'gingerbread':
                pygame.draw.ellipse(self.screen, n.color, (nx, ny, n.rect.width, n.rect.height))
                pygame.draw.rect(self.screen, (33,33,33), (nx, ny - 10, n.rect.width, 4))
                pygame.draw.rect(self.screen, (239, 68, 68), (nx, ny - 10, int(n.rect.width * (n.health / n.max_health)), 4))
            else:
                pygame.draw.rect(self.screen, n.color, (nx, ny, n.rect.width, n.rect.height))
                pygame.draw.rect(self.screen, (255, 255, 255), (nx + 5, ny + 5, 6, 6))

        for p in self.projectiles:
            if p.owner == 'npc':
                pygame.draw.circle(self.screen, (217, 119, 6), (p.rect.centerx - Camera.camera_x, p.rect.centery - Camera.camera_y), p.rect.width // 2)

        now = time.time() * 1000
        is_visible = now >= self.player.invulnerable_until or int(now / 150) % 2 == 0
        if is_visible:
            px = self.player.rect.x - Camera.camera_x
            py = self.player.rect.y - Camera.camera_y
            pygame.draw.rect(self.screen, PLAYER_COLOR, (px, py, self.player.rect.width, self.player.rect.height))
            pygame.draw.rect(self.screen, (255, 255, 255), (px + (18 if self.player.direction == 'right' else 5), py + 10, 8, 8))

        Camera.draw_red_frame(self.screen, self.player, self.k_level)

        # Scale and blit virtual surface to real screen
        scaled_surf = pygame.transform.scale(self.screen, (WIDTH, HEIGHT))
        real_screen.blit(scaled_surf, (0, 0))

        # Restore self.screen to real_screen so UI draws natively
        self.screen = real_screen

        font = pygame.font.SysFont(None, 36)
        self.screen.blit(font.render(f"Hearts: {self.player.health}", True, (0, 0, 0)), (20, 20))
        self.screen.blit(font.render(f"Score: {self.player.score}", True, (0, 0, 0)), (150, 20))
        lvl_str = "Home" if self.k_level == 0 else str(self.k_level)
        self.screen.blit(font.render(f"Level: {lvl_str}", True, (0, 0, 0)), (300, 20))

        if self.state in ['menu', 'gameOver', 'win']:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))
            txt1 = "PIXEL QUEST" if self.state == 'menu' else ("GAME OVER" if self.state == 'gameOver' else "YOU WIN!")
            txt2 = "Press SPACE to start" if self.state == 'menu' else "Press R to retry"
            self.screen.blit(pygame.font.SysFont(None, 72).render(txt1, True, (255, 255, 255)), (WIDTH // 2 - 150, HEIGHT // 2 - 50))
            self.screen.blit(pygame.font.SysFont(None, 36).render(txt2, True, (200, 200, 200)), (WIDTH // 2 - 100, HEIGHT // 2 + 20))

        WriteLog.draw(self.screen)

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
                            self.load_level(self.k_level)
                            self.player.reset(50, 300, self.player.score, 3)
                        else:
                            self.k_level = 1
                            self.next_level = 2
                            self.load_level(1)
                            self.player.reset(50, 300)
                        self.state = 'playing'
                    
                    Camera.zoom_update(self.state, event.key)

            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    Game().run()
