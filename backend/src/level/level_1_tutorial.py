from src.constants import *
from src.item.item import Item
from src.npc.npc import NPC
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