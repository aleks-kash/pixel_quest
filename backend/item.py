import pygame

class Item:
    def __init__(self, x, y, type):
        w, h = (15, 15) if type == 'coin' else (20, 20)
        self.rect = pygame.Rect(x, y, w, h)
        self.type = type
        self.collected = False
