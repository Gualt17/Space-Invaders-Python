import pygame

PLAYER_BULLET_SPEED = 10
ENEMY_BULLET_SPEED = 8

ENEMY_SHOT_FREQUENCY = 30

class Shoot:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 4, 10)
        self.speed = PLAYER_BULLET_SPEED
        self.active = True
        self.color = (0, 255, 0)

    def update(self):
        self.rect.y -= self.speed
        if self.rect.bottom < 0:
            self.active = False

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)

class EnemyShot:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 4, 10)
        self.speed = ENEMY_BULLET_SPEED
        self.active = True
        self.color = (255, 255, 0)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > pygame.display.get_surface().get_height():
            self.active = False

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)