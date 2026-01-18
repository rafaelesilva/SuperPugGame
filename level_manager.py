import pygame
import random
from settings import *
from sprites import Platform, Enemy, Bone, Flag, Pigeon

class LevelManager:
    def __init__(self, game):
        self.game = game

    def create_level(self, difficulty):
        # Limpa sprites antigos se houver
        # (A limpeza geral já é feita no new_game, mas garantimos aqui)
        pass

        ground_y = HEIGHT - int(60 * SCALE)
        
        # Chão inicial seguro
        p = Platform(0, ground_y, int(WIDTH * 1.5), int(60 * SCALE))
        self.game.all_sprites.add(p)
        self.game.platforms.add(p)
        
        current_x = int(WIDTH * 1.5)
        
        # Ajuste de dificuldade na geração
        min_gap = int(50 * SCALE) + (difficulty * 5)
        max_gap = int(120 * SCALE) + (difficulty * 15) 
        if max_gap > 300 * SCALE: max_gap = 300 * SCALE

        segments = 15 + (difficulty * 2) 
        
        for i in range(segments):
            # 1. GERA PLATAFORMA
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
            
            p = Platform(current_x, plat_y, plat_w, int(60 * SCALE))
            self.game.all_sprites.add(p)
            self.game.platforms.add(p)
            
            # 2. GERA OSSOS (Comum a todas as fases)
            if random.random() > 0.5:
                num_bones = random.randint(1, 3)
                start_bone_x = current_x + int(50*SCALE)
                for b in range(num_bones):
                    bx = start_bone_x + (b * int(50*SCALE))
                    if bx < current_x + plat_w - int(50*SCALE): 
                        bone = Bone(bx, plat_y)
                        self.game.all_sprites.add(bone)
                        self.game.bones.add(bone)

            # 3. GERA INIMIGOS (Lógica por Fase)
            # Fase 1: Gato, Vaca, Guarda-chuva
            # Fase 2: Praia (Pombas e caranguejos/gatos)
            
            # Chance base de inimigo
            if random.random() > 0.4:
                ex = current_x + plat_w // 2
                ey = plat_y - int(150 * SCALE)
                
                enemy_type = 'gato' # Padrão
                
                if difficulty == 1:
                    enemy_type = random.choice(['gato', 'vaca', 'guarda_chuva'])
                    e = Enemy(ex, ey, enemy_type, self.game, platform=p)
                    self.game.all_sprites.add(e)
                    self.game.enemies.add(e)
                
                elif difficulty >= 2:
                    # Na fase 2 misturamos chao e ar
                    if random.random() < 0.5:
                        # Inimigo de chão
                        enemy_type = random.choice(['gato']) # Adicionar caranguejo depois se quiser
                        e = Enemy(ex, ey, enemy_type, self.game, platform=p)
                        self.game.all_sprites.add(e)
                        self.game.enemies.add(e)
                    else:
                        # INIMIGO AEREO (POMBA)
                        # A pomba spawna alto, independente da plataforma
                        py = random.randint(int(50*SCALE), int(200*SCALE))
                        # Posição X relativa à plataforma atual
                        px = current_x + random.randint(0, plat_w)
                        pomba = Pigeon(px, py, self.game)
                        self.game.all_sprites.add(pomba)
                        self.game.enemies.add(pomba)

            current_x += plat_w

        # Plataforma Final
        current_x += int(150 * SCALE)
        final_plat = Platform(current_x, ground_y, int(500 * SCALE), int(60 * SCALE))
        self.game.all_sprites.add(final_plat)
        self.game.platforms.add(final_plat)
        
        flag = Flag(current_x + int(400 * SCALE), ground_y)
        self.game.all_sprites.add(flag)
        self.game.flags.add(flag)
