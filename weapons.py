import pygame
from settings import *

# ATENÇÃO: Multiplicamos tamanho e velocidade pelo SCALE
WEAPONS_LIST = [
    {"name": "Osso", "color": (255, 255, 240), "damage": 2, "speed": 10 * SCALE, "size": (int(20*SCALE), int(10*SCALE))},
    {"name": "Laser", "color": (255, 0, 0), "damage": 5, "speed": 20 * SCALE, "size": (int(30*SCALE), int(5*SCALE))},
    {"name": "Bolinha", "color": (255, 255, 0), "damage": 3, "speed": 12 * SCALE, "size": (int(15*SCALE), int(15*SCALE))},
    {"name": "Fogo", "color": (255, 100, 0), "damage": 8, "speed": 8 * SCALE, "size": (int(20*SCALE), int(20*SCALE))},
    {"name": "Plasma", "color": (0, 255, 255), "damage": 4, "speed": 15 * SCALE, "size": (int(25*SCALE), int(25*SCALE))},
    {"name": "Raio", "color": (200, 100, 255), "damage": 10, "speed": 25 * SCALE, "size": (int(40*SCALE), int(5*SCALE))},
    {"name": "Gelo", "color": (200, 255, 255), "damage": 3, "speed": 12 * SCALE, "size": (int(18*SCALE), int(18*SCALE))},
    {"name": "Veneno", "color": (50, 255, 50), "damage": 2, "speed": 10 * SCALE, "size": (int(15*SCALE), int(15*SCALE))},
    {"name": "Pedra", "color": (100, 100, 100), "damage": 6, "speed": 12 * SCALE, "size": (int(20*SCALE), int(20*SCALE))},
    {"name": "Super Bark", "color": (255, 0, 255), "damage": 20, "speed": 6 * SCALE, "size": (int(50*SCALE), int(50*SCALE))}
]

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, weapon_idx):
        super().__init__()
        weapon = WEAPONS_LIST[weapon_idx]
        
        self.image = pygame.Surface(weapon['size'])
        self.image.fill(weapon['color'])
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        
        self.speed = weapon['speed'] * direction
        self.damage = weapon['damage']

    def update(self):
        self.rect.x += self.speed
        if self.rect.right < 0 or self.rect.left > WIDTH:
            self.kill()
