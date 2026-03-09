import pygame
from src.npc.npc import NPC

class Gingerbread(NPC):
    def __init__(self, x, y, w, h, vx, patrol_range):
        health = 2
        color = (139, 69, 19)
        npc_type = 'gingerbread'

        super().__init__(x, y, w, h, color, vx, npc_type, patrol_range, health)