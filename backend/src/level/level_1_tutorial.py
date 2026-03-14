import pygame

from src.constants import *
from src.item.item import Item
from src.npc.npc import NPC
from src.control.camera import Camera
from src.npc.enemy.red_patrol_unit import RedPatrolUnit
from src.platform.platform_obj import Platform

class Level1Tutorial:
    def __init__(self):
        self.platforms = []
        self.items = []
        self.npcs = []
        self.projectiles = []

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

    def draw_background(self, screen, cam_x):
        cam_y = Camera.camera_y
        h = HEIGHT - int(cam_y)

        screen.fill((224, 242, 254))
        for i in range(3):
            x = int((i * 500 - cam_x * 0.1) % 1500) - 500
            pygame.draw.polygon(screen, (147, 197, 253), [(x, h), (x + 250, h - 150), (x + 500, h)])
        for i in range(4):
            x = int((i * 400 - cam_x * 0.3) % 1600) - 400
            pygame.draw.polygon(screen, (96, 165, 250), [(x, h), (x + 200, h - 80), (x + 400, h)])
        for i in range(6):
            x = int((i * 350 - cam_x * 0.7) % 2100) - 350
            pygame.draw.ellipse(screen, (52, 211, 153), (x, h - 90, 120, 60))
