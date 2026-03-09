import pygame

class Projectile:
    def __init__(self, x, y, w, h, vx, owner, max_distance=350):
        self.rect = pygame.Rect(x, y, w, h)
        self.vx = vx
        self.owner = owner
        self.distance = 0
        self.max_distance = max_distance
