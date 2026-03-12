from src.constants import *

from src.platform.platform_obj import Platform
from src.npc.npc import NPC
from src.item.item import Item

class Level0Hub:
    def __init__(self):
        self.platforms = []
        self.items = []
        self.npcs = []
        self.projectiles = []

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