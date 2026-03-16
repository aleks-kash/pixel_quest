import pygame
from src.npc.npc import NPC

class Gingerbread(NPC):
    def __init__(self, x, y, speed, patrol_range):
        health = 2
        color = (139, 69, 19)
        npc_type = 'gingerbread'
        width = 32
        height = 32
        
        super().__init__(x, y, width, height, color, speed, npc_type, patrol_range, health)