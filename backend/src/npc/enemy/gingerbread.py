import pygame
import math

from src.npc.npc import NPC

class Gingerbread(NPC):
    def __init__(self, x, y, speed, patrol_range):
        health = 2
        color = (139, 69, 19)
        npc_type = 'gingerbread'
        width = 32
        height = 32

        # Цвета из вашего проекта
        self.body_color = (139, 69, 19)   # Коричневый
        self.eye_color = (255, 255, 255)  # Белый
        self.pupil_color = (0, 0, 0)      # Черный
        self.icing_color = (255, 255, 255)# Белая глазурь
        self.button_color = (16, 185, 129)# Зеленая пуговица
        self.headband_color = (239, 68, 68)# Красная повязка
        
        super().__init__(x, y, width, height, color, speed, npc_type, patrol_range, health)

    def update(self):
        # Логика патрулирования
        self.rect.x += self.vx
        if abs(self.rect.x - self.start_x) > self.patrol_range:
            self.vx *= -1 # Разворот

    def draw(self, surface, cam_x):
        time = pygame.time.get_ticks()
        
        # 0. Анимация: Парение + Наклон
        bob = math.sin(time / 200) * 5
        tilt = math.sin(time / 400) * 10 # Наклон в градусах
        
        # Создаем временную поверхность для персонажа, чтобы вращать его целиком
        sprite_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
        
        # Рисуем персонажа на этой поверхности
        # (координаты внутри sprite_surf)
        # draw_x, draw_y = 14, 14
        draw_x = self.rect.x - cam_x
        draw_y = self.rect.y + bob

        # 1. Руки (подняты вверх, как в оригинале)
        # Рисуем их как прямоугольники, повернутые или просто поднятые
        
        arm_width = 20
        hands_down = 8

        # позиция рук относительно тела с лева на право
        pos_l_hand_l = draw_x - 18 #8
        pos_l_hand_r = draw_x + 30 #30

        # позиция рук относительно тела с верху вниз
        pos_down_hand = draw_y + 5
        
        pygame.draw.rect(surface, self.body_color, (pos_l_hand_l, pos_down_hand, arm_width, hands_down), border_radius=5) # Левая
        pygame.draw.rect(surface, self.body_color, (pos_l_hand_r, pos_down_hand, arm_width, hands_down), border_radius=5) # Правая

        # 2. Тело (основная часть)
        pygame.draw.rect(surface, self.body_color, (draw_x, draw_y, 32, 32), border_radius=6)

        # 3. Красная повязка на голове
        pygame.draw.rect(surface, self.headband_color, (draw_x - 2, draw_y - 2, 36, 6))

        # 4. Глаза (большие белые)
        # Моргание: если остаток от деления времени на 3000 < 200, глаза закрыты
        is_blinking = (time % 3000) < 200
        
        if is_blinking:
            # Глаза закрыты (линии)
            pygame.draw.line(surface, (0, 0, 0), (draw_x + 6, draw_y + 12), (draw_x + 14, draw_y + 12), 2)
            pygame.draw.line(surface, (0, 0, 0), (draw_x + 18, draw_y + 12), (draw_x + 26, draw_y + 12), 2)
        else:
            # Глаза открыты
            pygame.draw.circle(surface, (255, 255, 255), (draw_x + 10, draw_y + 12), 5)
            pygame.draw.circle(surface, (255, 255, 255), (draw_x + 22, draw_y + 12), 5)
            pygame.draw.circle(surface, (0, 0, 0), (draw_x + 10, draw_y + 12), 2)
            pygame.draw.circle(surface, (0, 0, 0), (draw_x + 22, draw_y + 12), 2)

        # 5. Рот (зигзаг из линий)
        # Рисуем зигзаг как серию коротких линий
        mouth_y = draw_y + 20
        pygame.draw.line(surface, self.icing_color, (draw_x + 10, mouth_y), (draw_x + 14, mouth_y + 4), 2)
        pygame.draw.line(surface, self.icing_color, (draw_x + 14, mouth_y + 4), (draw_x + 18, mouth_y), 2)
        pygame.draw.line(surface, self.icing_color, (draw_x + 18, mouth_y), (draw_x + 22, mouth_y + 4), 2)

        # 6. Зеленая пуговица
        pygame.draw.circle(surface, self.button_color, (draw_x + 16, draw_y + 26), 4)