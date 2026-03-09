import pygame

class Platform:
    def __init__(self, x, y, w, h, color, type):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.type = type
