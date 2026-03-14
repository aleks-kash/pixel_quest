import pygame
import random
import time
import math

class LavaEffects:
    def __init__(self):
        self.particles = [] # Steam/smoke particles
        self.bubbles = []    # Bubbles on surface
        self.last_update = time.time() * 1000

    def update(self, platforms):
        now = time.time() * 1000
        dt = now - self.last_update
        self.last_update = now

        # 1. Update existing particles
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= dt
            if p['life'] <= 0:
                self.particles.remove(p)

        # 2. Update existing bubbles
        for b in self.bubbles[:]:
            b['timer'] += dt
            # Bubble expands then pops
            if b['timer'] > b['duration']:
                self.bubbles.remove(b)

        # 3. Spawn new effects over lava platforms
        for p in platforms:
            if p.type == 'lava':
                # chance to spawn steam
                if random.random() < 0.1:
                    self.particles.append({
                        'x': random.uniform(p.rect.left, p.rect.right),
                        'y': p.rect.top,
                        'vx': random.uniform(-0.5, 0.5),
                        'vy': random.uniform(-1.5, -0.5),
                        'life': random.uniform(500, 1500),
                        'size': random.uniform(2, 5)
                    })
                
                # chance to spawn a bubble
                if random.random() < 0.02:
                    self.bubbles.append({
                        'x': random.uniform(p.rect.left + 5, p.rect.right - 5),
                        'y': p.rect.top,
                        'timer': 0,
                        'duration': random.uniform(800, 1500),
                        'max_size': random.uniform(6, 12)
                    })

    def draw(self, screen, cam_x, cam_y):
        # Draw steam
        for p in self.particles:
            alpha = int((p['life'] / 1500) * 150)
            s = pygame.Surface((p['size']*2, p['size']*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (200, 200, 200, alpha), (p['size'], p['size']), p['size'])
            screen.blit(s, (p['x'] - cam_x - p['size'], p['y'] - cam_y - p['size']))

        # Draw bubbles
        for b in self.bubbles:
            progress = b['timer'] / b['duration']
            # Bubble grows then stays a bit then "pops" (disappears)
            size = b['max_size'] * math.sin(progress * math.pi)
            if size > 1:
                # Darker outline for bubble
                pygame.draw.circle(screen, (180, 50, 50), (int(b['x'] - cam_x), int(b['y'] - cam_y)), int(size), 1)
                # Lighter center
                pygame.draw.circle(screen, (255, 100, 100), (int(b['x'] - cam_x), int(b['y'] - cam_y)), int(size/2))
