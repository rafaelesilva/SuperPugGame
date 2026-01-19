import pygame
import sys
import os
import random 
import math 
from settings import *
from sprites import Player, Platform, Enemy, Explosion, Flag, Bone
from weapons import Projectile, WEAPONS_LIST, EnemyProjectile
from level_manager import LevelManager

GAME_FOLDER = os.path.dirname(__file__)
ASSETS_FOLDER = os.path.join(GAME_FOLDER, 'assets')

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        
        # --- UI & FONTES ---
        font_size = int(25 * SCALE) 
        try:
            self.font = pygame.font.SysFont("Arial", font_size, bold=True)
            self.title_font = pygame.font.SysFont("Arial", int(60 * SCALE), bold=True)
        except:
            self.font = pygame.font.Font(None, font_size)
            self.title_font = pygame.font.Font(None, int(60 * SCALE))
            
        self.padding = int(120 * SCALE) 
        self.btn_size = int(HEIGHT * 0.18) 
        
        self.setup_buttons()
        
        # --- CARREGAR IMAGEM DO MENU ---
        # Tenta carregar a imagem estilo Master System
        self.menu_bg_image = None
        try:
            bg_path = os.path.join(ASSETS_FOLDER, 'menu_bg.png')
            if os.path.exists(bg_path):
                img = pygame.image.load(bg_path).convert()
                self.menu_bg_image = pygame.transform.scale(img, (WIDTH, HEIGHT))
        except Exception as e:
            print(f"Erro ao carregar menu_bg: {e}")
        
        # --- MULTI-TOUCH ---
        self.fingers = {} 
        self.last_shot_time = 0
        self.shoot_delay = 250 

        # --- SISTEMA DE JOGO ---
        self.level = 1
        self.total_score = 0
        self.level_manager = LevelManager(self)
        self.game_mode = 'campaign' # 'campaign' ou 'mission'

        self.bg_parts = []
        self.bg_width = WIDTH
        self.bg_scroll = 0
        self.load_backgrounds()

        self.state = 'MENU'
        self.running = True

    def load_backgrounds(self):
        fname = f'fundo{self.level}.png'
        path = os.path.join(ASSETS_FOLDER, fname)
        self.bg_parts = []
        try:
            if os.path.exists(path):
                full_bg = pygame.image.load(path).convert()
                full_w = full_bg.get_width()
                full_h = full_bg.get_height()
                part_w = full_w // 3
                
                scale_ratio = HEIGHT / full_h
                new_w = int(part_w * scale_ratio)
                new_h = int(full_h * scale_ratio)
                
                for i in range(3):
                    part = full_bg.subsurface((part_w * i, 0, part_w, full_h))
                    self.bg_parts.append(pygame.transform.scale(part, (new_w, new_h)))
                
                self.bg_width = new_w 
            else:
                pass 
        except Exception as e:
            print(f"Erro BG: {e}")
            self.bg_parts = []

    def setup_buttons(self):
        # --- CONTROLES DE JOGO ---
        dpad_size = int(80 * SCALE)
        margin = int(20 * SCALE)
        base_y = HEIGHT - dpad_size - margin
        base_x = margin
        hitbox_pad = int(20 * SCALE)
        
        self.btn_left = pygame.Rect(base_x - hitbox_pad, base_y - hitbox_pad, dpad_size + hitbox_pad*2, dpad_size + hitbox_pad*2)
        x_right = base_x + dpad_size + 10
        self.btn_right = pygame.Rect(x_right - hitbox_pad, base_y - hitbox_pad, dpad_size + hitbox_pad*2, dpad_size + hitbox_pad*2)
        x_up = base_x + (dpad_size // 2) + 5
        y_up = base_y - dpad_size - 10
        self.btn_up = pygame.Rect(x_up - hitbox_pad, y_up - hitbox_pad, dpad_size + hitbox_pad*2, dpad_size + hitbox_pad*2)

        offset_da_borda = int(100 * SCALE) 
        target_center_x = WIDTH - (self.btn_size // 2) - offset_da_borda
        target_center_y = HEIGHT - (self.btn_size // 2) - int(self.padding * 0.5)
        self.btn_fire_center_point = (target_center_x, target_center_y)
        hitbox_size = int(self.btn_size * 1.8) 
        self.btn_fire = pygame.Rect(0, 0, hitbox_size, hitbox_size)
        self.btn_fire.center = self.btn_fire_center_point

        b_w = int(self.btn_size * 1.5) 
        b_h = int(self.btn_size * 0.6)
        self.btn_weapon = pygame.Rect(WIDTH - b_w - self.padding, int(self.padding * 0.2), b_w, b_h)
        self.btn_char = pygame.Rect(int(self.padding * 0.2), int(self.padding * 0.2), b_w, b_h)

        # --- BOTÕES DO MENU PRINCIPAL ---
        # Ajustei a posição para não tapar a arte (jogando mais para baixo)
        menu_btn_w = int(WIDTH * 0.35)
        menu_btn_h = int(HEIGHT * 0.12)
        center_x = WIDTH // 2 - menu_btn_w // 2
        
        # Posições ajustadas para o estilo capa de jogo (botões na parte inferior ou meio)
        self.btn_campanha = pygame.Rect(center_x, HEIGHT * 0.65, menu_btn_w, menu_btn_h)
        self.btn_missao = pygame.Rect(center_x, HEIGHT * 0.80, menu_btn_w, menu_btn_h)

        # --- BOTÕES DE SELEÇÃO DE FASE (1 a 5) ---
        self.level_buttons = []
        cols = 3
        start_x = WIDTH * 0.2
        start_y = HEIGHT * 0.3
        gap_x = int(50 * SCALE)
        btn_lvl_size = int(80 * SCALE)
        
        for i in range(5): 
            row = i // cols
            col = i % cols
            x = start_x + col * (btn_lvl_size + gap_x)
            y = start_y + row * (btn_lvl_size + gap_x)
            rect = pygame.Rect(x, y, btn_lvl_size, btn_lvl_size)
            self.level_buttons.append({'rect': rect, 'level': i+1})

        self.btn_back = pygame.Rect(WIDTH - int(150*SCALE), int(20*SCALE), int(130*SCALE), int(50*SCALE))

    def new_game(self):
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.bullets_enemy = pygame.sprite.Group()
        self.flags = pygame.sprite.Group()
        self.bones = pygame.sprite.Group() 
        
        self.load_backgrounds()
        self.bg_scroll = 0

        self.level_manager.create_level(difficulty=self.level)
        
        self.player = Player(self)
        self.all_sprites.add(self.player)
        self.state = 'PLAYING'

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            if self.state == 'MENU':
                self.events_menu()
                self.draw_menu()
            elif self.state == 'MISSION_SELECT':
                self.events_mission_select()
                self.draw_mission_select()
            elif self.state == 'PLAYING':
                self.events()
                self.update()
                self.draw()

    def events_menu(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.FINGERDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                if event.type == pygame.FINGERDOWN:
                    x = int(event.x * WIDTH)
                    y = int(event.y * HEIGHT)
                else:
                    x, y = event.pos

                if self.btn_campanha.collidepoint(x, y):
                    self.game_mode = 'campaign'
                    self.level = 1
                    self.total_score = 0
                    self.new_game()
                elif self.btn_missao.collidepoint(x, y):
                    self.state = 'MISSION_SELECT'

    def draw_menu(self):
        # 1. Desenha o fundo
        if self.menu_bg_image:
            self.screen.blit(self.menu_bg_image, (0, 0))
        else:
            self.screen.fill((100, 149, 237)) # Fallback Azul
            
            # Só desenha o título via código se NÃO tiver imagem
            title_text = "SUPER PUG GAME"
            t_w, t_h = self.title_font.size(title_text)
            t_pos = (WIDTH//2 - t_w//2, HEIGHT * 0.15)
            shadow = self.title_font.render(title_text, True, (0, 0, 0))
            self.screen.blit(shadow, (t_pos[0] + 5, t_pos[1] + 5))
            title = self.title_font.render(title_text, True, (255, 255, 0))
            self.screen.blit(title, t_pos)
        
        # 2. Botões (Usei alpha maior para destacar em cima da arte)
        # Se a imagem for muito poluída, aumente o alpha (ex: 200 ou 220)
        self.draw_transparent_btn(self.btn_campanha, "MODO CAMPANHA", color=(255, 255, 0), alpha=200, font_scale=1.1)
        self.draw_transparent_btn(self.btn_missao, "SELEÇÃO DE FASE", color=(255, 255, 255), alpha=200, font_scale=1.1)
            
        pygame.display.flip()

    def events_mission_select(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.FINGERDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                if event.type == pygame.FINGERDOWN:
                    x = int(event.x * WIDTH)
                    y = int(event.y * HEIGHT)
                else:
                    x, y = event.pos

                if self.btn_back.collidepoint(x, y):
                    self.state = 'MENU'
                    return

                for btn in self.level_buttons:
                    if btn['rect'].collidepoint(x, y):
                        self.game_mode = 'mission'
                        self.level = btn['level']
                        self.total_score = 0
                        self.new_game()

    def draw_mission_select(self):
        # Fundo escuro para a seleção (ou poderia usar a mesma imagem com blur/escurecida)
        self.screen.fill((40, 40, 60)) 
        
        title = self.font.render("ESCOLHA A MISSÃO:", True, (255, 255, 255))
        self.screen.blit(title, (WIDTH * 0.1, HEIGHT * 0.15))
        
        self.draw_transparent_btn(self.btn_back, "VOLTAR", color=(255, 100, 100), alpha=200)

        for btn in self.level_buttons:
            rect = btn['rect']
            lvl = btn['level']
            # Cores diferentes para destacar botões de fase
            self.draw_transparent_btn(rect, str(lvl), color=(100, 255, 100), alpha=150, font_scale=1.5)

        pygame.display.flip()

    def events(self):
        touch_left = False
        touch_right = False
        touch_up = False
        holding_fire = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.FINGERDOWN or event.type == pygame.FINGERMOTION:
                x = int(event.x * WIDTH)
                y = int(event.y * HEIGHT)
                self.fingers[event.finger_id] = (x, y)
                
                if event.type == pygame.FINGERDOWN:
                    if self.btn_weapon.collidepoint((x, y)):
                        self.player.weapon_index = (self.player.weapon_index + 1) % len(WEAPONS_LIST)
                    elif self.btn_char.collidepoint((x, y)):
                        self.player.next_character()

            elif event.type == pygame.FINGERUP:
                if event.finger_id in self.fingers:
                    del self.fingers[event.finger_id]

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if self.btn_up.collidepoint((mx, my)): self.player.jump()

        for finger_pos in self.fingers.values():
            if self.btn_left.collidepoint(finger_pos): touch_left = True
            if self.btn_right.collidepoint(finger_pos): touch_right = True
            if self.btn_up.collidepoint(finger_pos): touch_up = True
            if self.btn_fire.collidepoint(finger_pos): holding_fire = True
        
        if not self.fingers:
            mouse_pressed = pygame.mouse.get_pressed()[0]
            if mouse_pressed:
                mx, my = pygame.mouse.get_pos()
                if self.btn_left.collidepoint((mx, my)): touch_left = True
                elif self.btn_right.collidepoint((mx, my)): touch_right = True
                if self.btn_fire.collidepoint((mx, my)): holding_fire = True
                if self.btn_up.collidepoint((mx, my)): touch_up = True
            
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]: touch_left = True
            if keys[pygame.K_RIGHT]: touch_right = True
            if keys[pygame.K_SPACE] or keys[pygame.K_UP]: touch_up = True

        self.player.update_touch(touch_left, touch_right)
        
        if touch_up: self.player.jump()
            
        if holding_fire:
            now = pygame.time.get_ticks()
            if now - self.last_shot_time > self.shoot_delay:
                self.shoot()
                self.last_shot_time = now

    def shoot(self):
        dir = 1 if self.player.facing_right else -1
        b = Projectile(self.player.rect.centerx, self.player.rect.centery, dir, self.player.weapon_index)
        self.all_sprites.add(b)
        self.bullets.add(b)

    def update(self):
        self.all_sprites.update()
        
        if self.player.rect.right >= WIDTH * 0.4:
            scroll = self.player.rect.right - (WIDTH * 0.4)
            self.player.rect.right = WIDTH * 0.4 
            self.bg_scroll += scroll 
            
            for sprite in self.all_sprites:
                if sprite != self.player:
                    sprite.rect.x -= scroll

        hits = pygame.sprite.spritecollide(self.player, self.bones, True)
        for bone in hits: self.total_score += 50 

        if pygame.sprite.spritecollide(self.player, self.flags, False):
            self.total_score += 1000
            self.show_level_screen(f"NIVEL {self.level} COMPLETO!")
            
            if self.game_mode == 'campaign':
                self.level += 1 
                self.new_game()
            else:
                self.state = 'MISSION_SELECT'

        if self.player.rect.top > HEIGHT: 
            self.game_over_logic()

        hits = pygame.sprite.spritecollide(self.player, self.bullets_enemy, True)
        if hits:
            self.player.hp -= 10

        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, True)
        for enemy, bullets_list in hits.items():
            for b in bullets_list:
                enemy.hp -= b.damage
                if enemy.hp <= 0:
                    expl = Explosion(enemy.rect.center)
                    self.all_sprites.add(expl)
                    enemy.kill()
                    self.total_score += 100 

        hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        if hits:
            self.player.hp -= 1
            if self.player.rect.x < hits[0].rect.x: self.player.rect.x -= int(20*SCALE)
            else: self.player.rect.x += int(20*SCALE)

        if self.player.hp <= 0:
            self.game_over_logic()

    def game_over_logic(self):
        if self.game_mode == 'campaign':
            self.level = 1
            self.total_score = 0
            self.state = 'MENU'
        else:
            self.state = 'MISSION_SELECT'

    def draw_transparent_btn(self, rect, text, color=(255, 255, 255), alpha=80, font_scale=1.0):
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, alpha), s.get_rect(), border_radius=15)
        pygame.draw.rect(s, color, s.get_rect(), 2, border_radius=15)
        
        if font_scale != 1.0:
            cur_font = pygame.font.Font(None, int(30 * SCALE * font_scale))
        else:
            cur_font = self.font

        txt_surf = cur_font.render(text, True, color)
        txt_rect = txt_surf.get_rect(center=(rect.width//2, rect.height//2))
        s.blit(txt_surf, txt_rect)
        self.screen.blit(s, rect.topleft)

    def draw(self):
        self.screen.fill((135, 206, 235))
        
        if self.bg_parts:
            part_w = self.bg_width
            start_scroll = self.bg_scroll
            first_tile_idx = int(start_scroll // part_w)
            tile_offset = start_scroll % part_w
            draw_x = -tile_offset
            current_idx = first_tile_idx
            
            while draw_x < WIDTH:
                img_idx = current_idx % 3
                self.screen.blit(self.bg_parts[img_idx], (draw_x, 0))
                draw_x += part_w
                current_idx += 1
        
        self.all_sprites.draw(self.screen)
        
        # HUD
        s_txt = self.font.render(f"SCORE: {self.total_score}", True, (255, 255, 255))
        mode_txt = "CAMPAIGN" if self.game_mode == 'campaign' else "MISSION"
        l_txt = self.font.render(f"LVL: {self.level} | {mode_txt}", True, (255, 255, 0))
        
        self.screen.blit(s_txt, (WIDTH//2 - s_txt.get_width()//2, 10))
        gap = s_txt.get_height() + 5
        self.screen.blit(l_txt, (WIDTH//2 - l_txt.get_width()//2, 10 + gap))

        # CONTROLES
        BTN_ALPHA = 80 
        self.draw_transparent_btn(self.btn_left, "<", alpha=BTN_ALPHA)  
        self.draw_transparent_btn(self.btn_right, ">", alpha=BTN_ALPHA)
        self.draw_transparent_btn(self.btn_up, "^", alpha=BTN_ALPHA)

        # Botão Tiro
        visual_size = int(self.btn_size * 1.2) 
        surf = pygame.Surface((visual_size, visual_size), pygame.SRCALPHA)
        center = (visual_size // 2, visual_size // 2)
        radius = visual_size // 2
        pygame.draw.circle(surf, (0, 0, 0, BTN_ALPHA), center, radius)
        pygame.draw.circle(surf, (255, 255, 255), center, radius, 2)
        txt = self.font.render("TIRO", True, (255, 255, 255))
        txt_rect = txt.get_rect(center=center)
        surf.blit(txt, txt_rect)
        final_rect = surf.get_rect(center=self.btn_fire_center_point)
        self.screen.blit(surf, final_rect)

        # Menus Superiores
        w_name = WEAPONS_LIST[self.player.weapon_index]['name']
        self.draw_transparent_btn(self.btn_weapon, w_name, alpha=BTN_ALPHA)
        
        c_name = self.player.char_list[self.player.char_index].upper()
        self.draw_transparent_btn(self.btn_char, c_name, alpha=BTN_ALPHA)

        self.draw_health_bar(self.screen, self.player.rect.x, self.player.rect.y - 15, self.player.hp)
        
        pygame.display.flip()

    def show_level_screen(self, text):
        self.screen.fill((0,0,0))
        txt = self.font.render(text, True, (255,255,255))
        self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))
        pygame.display.flip()
        pygame.time.delay(2000)
    
    def draw_health_bar(self, surface, x, y, pct):
        if pct < 0: pct = 0
        BAR_LENGTH = int(80 * SCALE)
        BAR_HEIGHT = int(8 * SCALE)
        fill = (pct / 100) * BAR_LENGTH
        col = (0, 255, 0) if pct >= 30 else (255, 0, 0)
        pygame.draw.rect(surface, col, (x, y, fill, BAR_HEIGHT))
        pygame.draw.rect(surface, (255, 255, 255), (x, y, BAR_LENGTH, BAR_HEIGHT), 2)

if __name__ == "__main__":
    g = Game()
    g.run()
