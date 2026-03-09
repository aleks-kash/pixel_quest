import pygame

GRAVITY = 0.6
FRICTION = 0.85
JUMP_FORCE = -12
SPEED = 0.8
MAX_SPEED = 5

class Player:
    def __init__(self):
        self.reset()

    def reset(self, x=50, y=300, score=0, health=3):
        self.rect = pygame.Rect(x, y, 32, 48)
        self.vx = 0
        self.vy = 0
        self.is_jumping = False
        self.on_ground = False
        self.health = health
        self.score = score
        self.direction = 'right'
        self.invulnerable_until = 0
        self.drop_timer = 0
        self.knockback = 0

    def update(self, keys, platforms):
        # Movement
        if self.knockback > 0:
            self.knockback -= 1
        else:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.vx -= SPEED
                self.direction = 'left'
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.vx += SPEED
                self.direction = 'right'
        
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vy = JUMP_FORCE
            self.on_ground = False
            self.is_jumping = True

        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.on_ground:
            is_on_wood = any(
                p.type == 'wood' and
                self.rect.colliderect(pygame.Rect(p.rect.x, p.rect.y - 2, p.rect.width, 4))
                for p in platforms
            )
            if is_on_wood:
                self.drop_timer = 15
                self.on_ground = False
                self.rect.y += 5

        # Physics
        self.vx *= FRICTION
        self.vy += GRAVITY
        self.rect.x += self.vx
        self.rect.y += self.vy

        # Clamp speed
        if abs(self.vx) > MAX_SPEED:
            self.vx = MAX_SPEED if self.vx > 0 else -MAX_SPEED

        # Collision
        self.on_ground = False
        if self.drop_timer > 0:
            self.drop_timer -= 1

        for plat in platforms:
            if plat.type == 'wood' and self.drop_timer > 0:
                continue
            if plat.type == 'wood' and self.vy < 0:
                continue

            if self.rect.colliderect(plat.rect):
                if plat.type == 'goal':
                    return "goal"
                if plat.type == 'lava':
                    return "lava"
                
                if self.vy > 0 and self.rect.bottom - self.vy <= plat.rect.bottom:
                    if plat.type in ['solid', 'wood']:
                        if self.rect.bottom - self.vy <= plat.rect.top:
                            self.rect.bottom = plat.rect.top
                            self.vy = 0
                            self.on_ground = True
                            self.is_jumping = False
        return None
