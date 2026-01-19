import pygame
import os
import random
import math 
from settings import *
from weapons import EnemyProjectile

GAME_FOLDER = os.path.dirname(__file__)
ASSETS_FOLDER = os.path.join(GAME_FOLDER, 'assets')

class Player(pygame.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.facing_right = True
        self.char_list = ['dino', 'bob', 'nina'] 
        self.char_index = 0
        
        self.hp = 100
        self.max_hp = 100
        self.size = (int(60 * SCALE), int(50 * SCALE))

        # --- SISTEMA DE ANIMAÇÃO ---
        self.animation_db = {} # Dicionário que guarda LISTAS de frames
        self.frame_index = 0   # Qual frame da lista estamos mostrando agora
        self.animation_speed = 150 # Velocidade da troca em milissegundos (quanto menor, mais rápido)
        self.last_frame_update = pygame.time.get_ticks()
        
        # Tenta carregar 4 frames de caminhada para cada personagem
        num_frames_to_load = 4 
        
        for name in self.char_list:
            frames = []
            loaded_walking = False
            
            # 1. Tenta carregar a sequência: nome_walk1.png, nome_walk2.png, etc.
            for i in range(1, num_frames_to_load + 1):
                path = os.path.join(ASSETS_FOLDER, f'{name}_walk{i}.png')
                if os.path.exists(path):
                    try:
                        img = pygame.image.load(path).convert_alpha()
                        img = pygame.transform.scale(img, self.size)
                        frames.append(img)
                        loaded_walking = True
                    except:
                        print(f"Erro ao carregar frame: {path}")

            # 2. Fallback: Se não achou nenhuma imagem de 'walk', carrega a estática antiga
            if not frames or not loaded_walking:
                print(f"Aviso: Animação não encontrada para {name}. Usando imagem estática.")
                frames = [] # Garante lista limpa
                path_static = os.path.join(ASSETS_FOLDER, f'{name}.png')
                try:
                    img = pygame.image.load(path_static).convert_alpha()
                    img = pygame.transform.scale(img, self.size)
                    # Adiciona a mesma imagem várias vezes para a lista não ficar vazia
                    for _ in range(num_frames_to_load):
                        frames.append(img)
                except:
                     # Último caso: quadrado roxo se não tiver NADA
                    surf = pygame.Surface(self.size)
                    surf.fill((255, 0, 255)) 
                    for _ in range(num_frames_to_load):
                        frames.append(surf)

            self.animation_db[name] = frames

        # Define a imagem inicial
        self.image_orig = self.animation_db[self.char_list[self.char_index]][0]
        self.image = self.image_orig
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 4, HEIGHT / 2)
        
        self.vel_y = 0
        self.on_ground = False
        self.is_moving = False # Nova flag para saber se está andando
        self.weapon_index = 0

    def next_character(self):
        self.char_index = (self.char_index + 1) % len(self.char_list)
        # Reseta o frame ao trocar de personagem
        self.frame_index = 0
        self.update_image_frame()

    # Nova função para pegar o frame correto e espelhar se necessário
    def update_image_frame(self):
        name = self.char_list[self.char_index]
        # Pega o frame atual da lista usando o índice
        current_frame = self.animation_db[name][self.frame_index]
        
        if self.facing_right:
            self.image = current_frame
        else:
            self.image = pygame.transform.flip(current_frame, True, False)

    # Função que roda todo loop para calcular a animação
    def animate(self):
        now = pygame.time.get_ticks()
        
        # Só anima se estiver se movendo E no chão
        if self.is_moving and self.on_ground:
            if now - self.last_frame_update > self.animation_speed:
                self.last_frame_update = now
                # Avança para o próximo frame, e volta pro 0 se chegar no fim da lista (loop)
                name = self.char_list[self.char_index]
                total_frames = len(self.animation_db[name])
                self.frame_index = (self.frame_index + 1) % total_frames
                self.update_image_frame()
        else:
            # Se parou ou pulou, volta para o frame 0 (pose parada)
            if self.frame_index != 0:
                self.frame_index = 0
                self.update_image_frame()

    def update_touch(self, left, right):
        # Reseta a flag de movimento
        self.is_moving = False
        
        if left:
            self.rect.x -= PLAYER_SPEED
            self.facing_right = False
            self.is_moving = True
        if right:
            self.rect.x += PLAYER_SPEED
            self.facing_right = True
            self.is_moving = True
            
        # Se mudou de direção instantaneamente, atualiza a imagem já
        if (left or right) and self.on_ground:
             self.update_image_frame()

    def update(self):
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        
        # Reseta a flag antes da colisão
        self.on_ground = False 
        hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
        if hits:
            # Verifica se está caindo sobre a plataforma (não batendo de baixo para cima)
            if self.vel_y >= 0 and self.rect.bottom < hits[0].rect.bottom + 10: 
                self.rect.bottom = hits[0].rect.top
                self.vel_y = 0
                self.on_ground = True
        
        if self.rect.left < 0: self.rect.left = 0
        
        # Chama a lógica de animação
        self.animate()

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_FORCE
            self.on_ground = False
            # Opcional: Ao pular, força o frame 0 ou um frame de pulo específico
            self.frame_index = 0
            self.update_image_frame()

# --- DEMAIS CLASSES PERMANECEM IGUAIS ---
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, texture_name='chao.png'):
        super().__init__()
        self.image = pygame.Surface((w, h))
        path = os.path.join(ASSETS_FOLDER, texture_name)
        
        try:
            tile_img = pygame.image.load(path).convert_alpha()
            tile_size = int(50 * SCALE)
            tile_img = pygame.transform.scale(tile_img, (tile_size, tile_size))
            
            for i in range(0, w, tile_size):
                self.image.blit(tile_img, (i, 0))
                if h > tile_size:
                    if 'chao2' in texture_name:
                        fill_color = (194, 178, 128)
                    else:
                        fill_color = (101, 67, 33)
                    brown = pygame.Rect(i, tile_size, tile_size, h - tile_size)
                    pygame.draw.rect(self.image, fill_color, brown)
        except:
            self.image.fill((101, 67, 33))
            pygame.draw.rect(self.image, (0, 255, 0), (0, 0, w, int(10*SCALE)))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Flag(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        path = os.path.join(ASSETS_FOLDER, 'bandeira.png')
        size = (int(60 * SCALE), int(80 * SCALE))
        try:
            self.image = pygame.image.load(path).convert_alpha()
            self.image = pygame.transform.scale(self.image, size)
        except:
            self.image = pygame.Surface(size)
            self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.bottom = y

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, type_name, game, platform=None):
        super().__init__()
        self.game = game
        self.platform = platform 
        self.type = type_name
        self.vel_y = 0 
        
        if self.type == 'gato': base_size = (50, 40); base_speed = 3
        elif self.type == 'vaca': base_size = (70, 60); base_speed = 1
        elif self.type == 'caranguejo': base_size = (45, 35); base_speed = 2
        else: base_size = (40, 60); base_speed = 2

        self.size = (int(base_size[0] * SCALE), int(base_size[1] * SCALE))
        self.speed = base_speed * SCALE
        self.hp = 10 

        path = os.path.join(ASSETS_FOLDER, f'{self.type}.png')
        try:
            img = pygame.image.load(path).convert_alpha()
            self.image_right = pygame.transform.scale(img, self.size)
            self.image_left = pygame.transform.flip(self.image_right, True, False)
        except:
            surf = pygame.Surface(self.size)
            surf.fill((255, 0, 0))
            self.image_left = surf
            self.image_right = surf

        self.direction = -1 
        self.image = self.image_left
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y 

    def update(self):
        self.rect.x += self.speed * self.direction
        
        if self.type != 'guarda_chuva' and self.platform:
            if self.rect.left < self.platform.rect.left:
                self.rect.left = self.platform.rect.left
                self.direction = 1
            elif self.rect.right > self.platform.rect.right:
                self.rect.right = self.platform.rect.right
                self.direction = -1

        if self.type != 'guarda_chuva':
            self.vel_y += GRAVITY
            self.rect.y += self.vel_y
            hits = pygame.sprite.spritecollide(self, self.game.platforms, False)
            if hits:
                if self.vel_y > 0:
                    self.rect.bottom = hits[0].rect.top
                    self.vel_y = 0
        else:
            self.rect.y += random.choice([-2, 2])

        if self.direction == 1: self.image = self.image_right
        else: self.image = self.image_left
        
        if self.rect.top > HEIGHT: self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center):
        super().__init__()
        path = os.path.join(ASSETS_FOLDER, 'explosao_strip.png')
        self.frames = []
        exp_size = (int(80 * SCALE), int(80 * SCALE))
        try:
            sheet = pygame.image.load(path).convert_alpha()
            w, h = sheet.get_size()
            if w > h: 
                frame_width = h 
                num_frames = w // h
                for i in range(num_frames):
                    frame = sheet.subsurface((i * frame_width, 0, frame_width, h))
                    frame = pygame.transform.scale(frame, exp_size)
                    self.frames.append(frame)
            else:
                self.frames.append(pygame.transform.scale(sheet, exp_size))
        except:
            img = pygame.Surface(exp_size); img.fill((255,100,0))
            self.frames.append(img)
            
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=center)
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
            else:
                self.kill()

class Bone(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        path = os.path.join(ASSETS_FOLDER, 'ossinho.png')
        self.size = (int(15 * SCALE), int(15 * SCALE))
        try:
            self.image = pygame.image.load(path).convert_alpha()
            self.image = pygame.transform.scale(self.image, self.size)
        except:
            self.image = pygame.Surface(self.size)
            self.image.fill((255, 255, 255)) 
            
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y - int(10 * SCALE)
        
        self.y_start = self.rect.y
        self.float_offset = 0

    def update(self):
        self.float_offset += 0.1
        self.rect.y = self.y_start + int(5 * math.sin(self.float_offset))

class Pigeon(pygame.sprite.Sprite):
    def __init__(self, x, y, game):
        super().__init__()
        self.game = game
        self.size = (int(60 * SCALE), int(40 * SCALE))
        self.hp = 15
        
        path = os.path.join(ASSETS_FOLDER, 'pomba.png')
        try:
            img = pygame.image.load(path).convert_alpha()
            self.image_orig = pygame.transform.scale(img, self.size)
        except:
            self.image_orig = pygame.Surface(self.size)
            self.image_orig.fill((150, 150, 150))
            pygame.draw.rect(self.image_orig, (200, 200, 200), (10, 10, 30, 10))

        self.image = self.image_orig
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.speed = 4 * SCALE
        self.direction = -1 
        
        self.last_shot = 0
        self.shot_delay = 2000

    def update(self):
        self.rect.x += self.speed * self.direction
        
        if self.rect.right < 0:
            self.direction = 1
            self.image = pygame.transform.flip(self.image_orig, True, False)
        elif self.rect.left > WIDTH + 100:
            self.direction = -1
            self.image = self.image_orig

        self.rect.y += math.sin(pygame.time.get_ticks() * 0.005) * 2

        now = pygame.time.get_ticks()
        if 0 < self.rect.centerx < WIDTH:
            if now - self.last_shot > self.shot_delay:
                self.last_shot = now
                if random.random() > 0.3:
                    poop = EnemyProjectile(self.rect.centerx, self.rect.bottom)
                    self.game.all_sprites.add(poop)
                    self.game.bullets_enemy.add(poop)
