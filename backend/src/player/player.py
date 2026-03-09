import pygame

from src.constants import GRAVITY, FRICTION, JUMP_FORCE, SPEED, MAX_SPEED

class Player:
    def __init__(self):
        self.reset()

    def reset(self, x=50, y=300, score=0, health=3):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 32, 48)
        self.vx = 0
        self.vy = 0
        self.width = 32
        self.height = 48    
        self.color = '#3B82F6'
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

        # 2. Physics
        self.vx *= FRICTION
        # Clamp speed
        if abs(self.vx) > MAX_SPEED:
            self.vx = MAX_SPEED if self.vx > 0 else -MAX_SPEED

        # --- X Movement and Collision ---
        self.x += self.vx
        self.rect.x = int(self.x)

        for plat in platforms:
            if plat.type in ['goal', 'lava']:
                if self.rect.colliderect(plat.rect):
                    return plat.type # Return early if hit goal or lava
            
            if plat.type == 'wood':
                continue # Ignore X collision for wood
                
            if plat.type == 'solid' and self.rect.colliderect(plat.rect):
                if self.vx > 0: # Moving right
                    self.rect.right = plat.rect.left
                    self.x = float(self.rect.x)
                    self.vx = 0
                elif self.vx < 0: # Moving left
                    self.rect.left = plat.rect.right
                    self.x = float(self.rect.x)
                    self.vx = 0

        # --- Y Movement and Collision ---
        self.vy += GRAVITY
        self.y += self.vy
        self.rect.y = int(self.y)
        if abs(self.vx) > MAX_SPEED:
            self.vx = MAX_SPEED if self.vx > 0 else -MAX_SPEED

        # 3. Collision Detection (Platforms)
        self.on_ground = False
        if self.drop_timer > 0:
            self.drop_timer -= 1

        for plat in platforms:
            if plat.type == 'wood' and self.drop_timer > 0:
                continue
            if plat.type == 'wood' and self.vy < 0:
                continue

            if self.rect.colliderect(plat.rect):
                if plat.type in ['goal', 'lava']:
                    return plat.type
                    
                if plat.type in ['solid', 'wood']:
                    if self.vy > 0: # Falling down
                        self.rect.bottom = plat.rect.top
                        self.y = float(self.rect.y)
                        self.vy = 0
                        self.on_ground = True
                        self.is_jumping = False
                    elif self.vy < 0 and plat.type == 'solid': # Jumping up and hitting ceiling
                        self.rect.top = plat.rect.bottom
                        self.y = float(self.rect.y)
                        self.vy = 0
                        
        return None
