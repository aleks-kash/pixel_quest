import math
import pygame

from src.constants import *
from src.npc.npc import NPC
from src.npc.enemy.red_patrol_unit import RedPatrolUnit
from src.item.item import Item
from src.platform.platform_obj import Platform
from src.control.camera import Camera

class Level2Night:
    def __init__(self):
        self.platforms = []
        self.items = []
        self.npcs = []
        self.projectiles = []

        self.platforms = [
            Platform(0, 400, 400, 50, PLATFORM_COLOR, 'solid'),
            Platform(500, 400, 400, 50, PLATFORM_COLOR, 'solid'),
            Platform(1000, 400, 400, 50, PLATFORM_COLOR, 'solid'),
            Platform(400, 320, 100, 20, WOOD_COLOR, 'wood'),
            Platform(900, 320, 100, 20, WOOD_COLOR, 'wood'),
            Platform(200, 250, 150, 20, WOOD_COLOR, 'wood'),
            Platform(600, 200, 150, 20, WOOD_COLOR, 'wood'),
            Platform(950, 250, 150, 20, WOOD_COLOR, 'wood'),
            Platform(1250, 200, 100, 20, WOOD_COLOR, 'wood'),
            Platform(1450, 150, 100, 20, GOAL_COLOR, 'goal'),
            Platform(400, 420, 100, 30, LAVA_COLOR, 'lava'),
            Platform(900, 420, 100, 30, LAVA_COLOR, 'lava'),
        ]
        
        for cx, cy in [(250, 210), (650, 160), (1150, 210)]:
            self.items.append(Item(cx, cy, 'coin'))
        self.items.append(Item(1300, 110, 'heart'))
        
        self.npcs = [
            NPC(300, 368, 32, 32, GINGERBREAD_COLOR, 1, 'gingerbread', 100, 2),
            NPC(700, 368, 32, 32, GINGERBREAD_COLOR, -1, 'gingerbread', 100, 2),
            NPC(1200, 368, 32, 32, GINGERBREAD_COLOR, 1, 'gingerbread', 100, 2),
            RedPatrolUnit(950, 218, 2, 60),
        ]

    def draw_background(self, screen, cam_x):
        """
        Отрисовывает фон второго уровня (ночное небо).
        screen: объект поверхности pygame
        cam_x: текущая позиция камеры
        width, height: размеры экрана
        """
        cam_y = Camera.camera_y
        height = HEIGHT - int(cam_y)

        # 1. Ночное небо (Dark Indigo)
        screen.fill((30, 27, 75)) #1E1B4B

        # 2. Звезды (с анимацией мерцания)
        if not hasattr(self, 'star_surfs'):
            self.star_surfs = {}
            for size in [1, 2]:
                s = pygame.Surface((size, size))
                s.fill((255, 255, 255))
                self.star_surfs[size] = s

        time = pygame.time.get_ticks()
        for i in range(50):
            x = (i * 12345) % WIDTH
            y = (i * 54321) % (height - 100)
            size = (i % 2) + 1
            
            # Мерцание
            alpha = int((0.5 + math.sin(time / 1000 + i) * 0.5) * 255)
            
            star_s = self.star_surfs[size]
            star_s.set_alpha(alpha)
            screen.blit(star_s, (x, y)) 

        # 3. Луна
        pygame.draw.circle(screen, (253, 230, 138), (WIDTH - 80, 60), 30)
        
        # Кратер на луне
        crater_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(crater_surf, (245, 158, 11, 50), (10, 10), 8)
        screen.blit(crater_surf, (WIDTH - 100, 40))

        # 4. Дальние горы (Parallax) (Deep Indigo)
        mountain_color = (49, 46, 129) #312E81
        m_spacings = [600, 700, 500]
        m_widths = [600, 800, 500]
        m_heights = [200, 250, 180]
        m_parallax = 0.1
        total_m_w = sum(m_spacings)
        m_offset = 0
        
        # Чтобы горы не "прыгали" при зацикливании, мы должны делать перенос за границами экрана.
        # Используем буфер (например, 600 пикселей), чтобы гора исчезала слева и появлялась справа вне видимости.
        buffer_m = 600 

        for i in range(len(m_spacings)):
            m_w = m_widths[i % len(m_widths)]
            m_h = m_heights[i % len(m_heights)]
            # (m_offset - cam_x * m_parallax + starting_pos + buffer) % total_w - buffer
            # Мы хотим, чтобы при cam_x=0 первая гора была на x=300.
            # Значит (0 + starting_pos + 600) % 1800 - 600 = 300 => starting_pos + 600 = 900 => starting_pos = 300.
            x = int((m_offset - cam_x * m_parallax + 300 + buffer_m) % total_m_w) - buffer_m
            
            points = [
                (x, height), 
                (x + m_w // 2, height - m_h), 
                (x + m_w, height)
            ]
            pygame.draw.polygon(screen, mountain_color, points)
            m_offset += m_spacings[i]

        # 5. Близкий темный лес (Силуэты)
        forest_color = (17, 24, 39)  # #111827
        tree_spacings = [200, 210, 190, 300, 220, 270, 190, 310]
        tree_heights = [120, 150, 100, 180, 130, 160, 110, 140]
        i_parallax = 0.6  # Сила параллакса
        total_forest_w = sum(tree_spacings)
        current_x_offset = 0
        buffer_f = 200 # Для леса достаточно меньшего буфера, так как деревья уже.
        
        for i, spacing in enumerate(tree_spacings):
            h_tree = tree_heights[i % len(tree_heights)]
            # Зацикливание леса за пределами экрана (от -buffer_f до total_forest_w - buffer_f)
            x = ((current_x_offset - cam_x * i_parallax + buffer_f) % total_forest_w) - buffer_f
            
            points = [
                (x, height), 
                (x + 50, height - h_tree), 
                (x + 100, height)
            ]
            pygame.draw.polygon(screen, forest_color, points)
            current_x_offset += spacing