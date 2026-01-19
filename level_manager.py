import pygame
import random
from settings import *
from sprites import Platform, Enemy, Bone, Flag, Pigeon

class LevelManager:
    def __init__(self, game):
        self.game = game

    def create_level(self, difficulty):
        # 1. ESCOLHA DA TEXTURA DO CHÃO BASEADA NO NÍVEL
        ground_img = 'chao.png' # Padrão (Grama)
        
        if difficulty == 2:
            ground_img = 'chao2.png' # Calçada de Copacabana
        elif difficulty >= 3:
            ground_img = 'chao.png' # Voltar para grama ou usar chao3 no futuro
            
        ground_y = HEIGHT - int(60 * SCALE)
        
        # 2. CRIAÇÃO DO CHÃO INICIAL (Passando texture_name)
        # O chão seguro do começo
        p = Platform(0, ground_y, int(WIDTH * 1.5), int(60 * SCALE), texture_name=ground_img)
        self.game.all_sprites.add(p)
        self.game.platforms.add(p)
        
        current_x = int(WIDTH * 1.5)
        
        # Ajuste de dificuldade (buracos maiores em níveis maiores)
        min_gap = int(50 * SCALE) + (difficulty * 5)
        max_gap = int(120 * SCALE) + (difficulty * 15) 
        if max_gap > 300 * SCALE: max_gap = 300 * SCALE

        segments = 15 + (difficulty * 2) 
        
        for i in range(segments):
            # --- GERA PLATAFORMA ---
            gap = random.randint(min_gap, max_gap)
            current_x += gap
            
            plat_w = random.randint(int(200 * SCALE), int(500 * SCALE))
            
            # Altura variada
            if random.random() > 0.3:
                plat_y = ground_y
            else:
                height_variance = int(50 * SCALE) * difficulty
                if height_variance > 250 * SCALE: height_variance = 250 * SCALE
                plat_y = ground_y - random.randint(int(50*SCALE), height_variance)
            
            # Cria a plataforma passando a textura correta
            p = Platform(current_x, plat_y, plat_w, int(60 * SCALE), texture_name=ground_img)
            self.game.all_sprites.add(p)
            self.game.platforms.add(p)
            
            # --- GERA OSSOS ---
            if random.random() > 0.5:
                num_bones = random.randint(1, 3)
                start_bone_x = current_x + int(50*SCALE)
                for b in range(num_bones):
                    bx = start_bone_x + (b * int(50*SCALE))
                    if bx < current_x + plat_w - int(50*SCALE): 
                        bone = Bone(bx, plat_y)
                        self.game.all_sprites.add(bone)
                        self.game.bones.add(bone)

            # --- GERA INIMIGOS ---
            if random.random() > 0.4:
                ex = current_x + plat_w // 2
                ey = plat_y - int(150 * SCALE)
                
                # Inimigos da Fase 1
                if difficulty == 1:
                    enemy_type = random.choice(['gato', 'vaca', 'guarda_chuva'])
                    e = Enemy(ex, ey, enemy_type, self.game, platform=p)
                    self.game.all_sprites.add(e)
                    self.game.enemies.add(e)
                
                # Inimigos da Fase 2+
                elif difficulty >= 2:
                    if random.random() < 0.5:
                        # Gatos continuam aparecendo no chão
                        enemy_type = random.choice(['gato']) 
                        e = Enemy(ex, ey, enemy_type, self.game, platform=p)
                        self.game.all_sprites.add(e)
                        self.game.enemies.add(e)
                    else:
                        # INIMIGO AÉREO (POMBA) - Mais comum na fase 2
                        py = random.randint(int(50*SCALE), int(200*SCALE))
                        px = current_x + random.randint(0, plat_w)
                        pomba = Pigeon(px, py, self.game)
                        self.game.all_sprites.add(pomba)
                        self.game.enemies.add(pomba)

            current_x += plat_w

        # 3. PLATAFORMA FINAL E BANDEIRA
        current_x += int(150 * SCALE)
        final_plat = Platform(current_x, ground_y, int(500 * SCALE), int(60 * SCALE), texture_name=ground_img)
        self.game.all_sprites.add(final_plat)
        self.game.platforms.add(final_plat)
        
        flag = Flag(current_x + int(400 * SCALE), ground_y)
        self.game.all_sprites.add(flag)
        self.game.flags.add(flag)
