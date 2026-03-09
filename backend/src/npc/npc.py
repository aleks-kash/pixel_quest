import pygame

class NPC:
    def __init__(self, x, y, w, h, color, vx, type, patrol_range, health):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.vx = vx
        self.type = type
        self.patrol_range = patrol_range
        self.start_x = x
        self.health = health
        self.max_health = health
        self.last_shoot_time = 0
        self.shoot_cooldown = 2000 if type == 'gingerbread' else 0
