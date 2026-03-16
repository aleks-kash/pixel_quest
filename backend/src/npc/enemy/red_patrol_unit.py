import pygame
from src.npc.npc import NPC

class RedPatrolUnit(NPC):
    def __init__(self, x, y, speed, patrol_range):
        health = 1
        color = (220, 38, 38)
        npc_type = 'enemy'
        width = 32
        height = 32

        super().__init__(x, y, width, height, color, speed, npc_type, patrol_range, health)