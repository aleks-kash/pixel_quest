import pygame

from src.constants import *
from src.npc.npc import NPC
from src.npc.enemy.red_patrol_unit import RedPatrolUnit
from src.item.item import Item
from src.platform.platform_obj import Platform
from src.control.camera import Camera

class Level2Night:
    def __init__(self):
        self.platforms = []
        self.items = []
        self.npcs = []
        self.projectiles = []

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
            RedPatrolUnit(950, 218, 2, 60),
        ]

    def draw_background(self, screen, cam_x):
        cam_y = Camera.camera_y
        h = HEIGHT - int(cam_y)

        screen.fill((30, 27, 75))
        for i in range(3):
            x = int((i * 600 - cam_x * 0.1) % 1800) - 600
            pygame.draw.polygon(screen, (49, 46, 129), [(x, h), (x + 300, h - 200), (x + 600, h)])
        for i in range(8):
            x = int((i * 200 - cam_x * 0.6) % 1600) - 200
            pygame.draw.polygon(screen, (17, 24, 39), [(x, h), (x + 50, h - 120), (x + 100, h)])
        for i in range(50):
            x = (i * 12345) % WIDTH
            y = (i * 54321) % (HEIGHT - 100) - int(cam_y)
            sz = (i % 2) + 1
            pygame.draw.rect(screen, (255, 255, 255), (x, y, sz, sz))
        pygame.draw.circle(screen, (253, 230, 138), (WIDTH - 80, 60 - int(cam_y)), 30)