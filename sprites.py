import pygame
import os
import random
from settings import *

GAME_FOLDER = os.path.dirname(__file__)
ASSETS_FOLDER = os.path.join(GAME_FOLDER, 'assets')

class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.facing_right = True
        self.char_list = ['dino', 'bob', 'nina'] 
        self.char_index = 0
        self.images_db = {} 
        
        # --- VIDA DO JOGADOR (NOVO) ---
        self.hp = 100
        self.max_hp = 100
        
        self.size = (int(60 * SCALE), int(50 * SCALE))
        
        for name in self.char_list:
            path = os.path.join(ASSETS_FOLDER, f'{name}.png')
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, self.size)
                self.images_db[name] = img
            except Exception:
                surf = pygame.Surface(self.size)
                surf.fill((255, 255, 0))
                self.images_db[name] = surf

        self.update_image()
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)
        self.vel_y = 0
        self.on_ground = False
        self.weapon_index = 0

    def next_character(self):
        self.char_index = (self.char_index + 1) % len(self.char_list)
        self.update_image()

    def update_image(self):
        name = self.char_list[self.char_index]
        self.image_orig = self.images_db[name]
        if self.facing_right:
            self.image = self.image_orig
        else:
            self.image = pygame.transform.flip(self.image_orig, True, False)

    def update_touch(self, left, right):
        if left:
            self.rect.x -= PLAYER_SPEED
            self.facing_right = False
            self.image = pygame.transform.flip(self.image_orig, True, False)
        if right:
            self.rect.x += PLAYER_SPEED
            self.facing_right = True
            self.image = self.image_orig

    def update(self):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        if hits:
            if self.vel_y > 0:
                self.rect.bottom = hits[0].rect.top
                self.vel_y = 0
                self.on_ground = True

        if self.rect.right > WIDTH: self.rect.right = WIDTH
        if self.rect.left < 0: self.rect.left = 0

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_FORCE
            self.on_ground = False

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.image = pygame.Surface((w, int(h * SCALE))) 
        self.image.fill(BROWN)
        pygame.draw.rect(self.image, GREEN, (0, 0, w, int(10 * SCALE)))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, type_name):
        super().__init__()
        self.type = type_name
        self.entered = False 
        
        if self.type == 'gato': base_size = (50, 40); base_speed = 4
        elif self.type == 'vaca': base_size = (70, 60); base_speed = 1
        elif self.type == 'guarda_chuva': base_size = (40, 60); base_speed = 2
        else: base_size = (50, 50); base_speed = 2

        self.size = (int(base_size[0] * SCALE), int(base_size[1] * SCALE))
        self.speed = base_speed * SCALE
        self.hp = 10 

        path = os.path.join(ASSETS_FOLDER, f'{self.type}.png')
        try:
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.scale(img, self.size)
            
            # Padroniza direção
            if self.type == 'gato' or self.type == 'guarda_chuva':
                img = pygame.transform.flip(img, True, False)
            
            self.image_right = img
            self.image_left = pygame.transform.flip(img, True, False)
            
        except:
            self.image_right = pygame.Surface(self.size)
            self.image_right.fill((255, 0, 0))
            self.image_left = self.image_right

        self.image = self.image_left
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = -1 

    def update(self):
        self.rect.x += self.speed * self.direction
        
        if self.direction == 1:
            self.image = self.image_right
        else:
            self.image = self.image_left

        if self.type == 'guarda_chuva':
            self.rect.y += random.choice([-2, 2])

        if not self.entered:
            if self.rect.right < WIDTH: self.entered = True
        else:
            if self.rect.right > WIDTH: self.direction = -1
            elif self.rect.left < 0: self.direction = 1

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        path = os.path.join(ASSETS_FOLDER, 'explosao_strip.png')
        self.frames = []
        exp_size = (int(80 * SCALE), int(80 * SCALE))
        
        try:
            sheet = pygame.image.load(path).convert_alpha()
            frame_width = sheet.get_height() 
            num_frames = sheet.get_width() // frame_width
            for i in range(num_frames):
                frame = sheet.subsurface((i * frame_width, 0, frame_width, frame_width))
                frame = pygame.transform.scale(frame, exp_size)
                self.frames.append(frame)
        except:
            img = pygame.Surface(exp_size)
            img.fill((255, 100, 0))
            self.frames.append(img)
            
        if not self.frames: self.frames.append(pygame.Surface(exp_size))

        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame_idx = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 60

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame_idx += 1
            if self.frame_idx < len(self.frames):
                self.image = self.frames[self.frame_idx]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center
            else:
                self.kill()
