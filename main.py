import pygame
import sys
import os
import random 
import math 
from settings import *
from sprites import Player, Platform, Enemy, Explosion, Flag, Bone
from weapons import Projectile, WEAPONS_LIST

GAME_FOLDER = os.path.dirname(__file__)
ASSETS_FOLDER = os.path.join(GAME_FOLDER, 'assets')

class Game:
    def __init__(self):
        pygame.init()
        pygame.mouse.set_visible(False)
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        
        # --- UI & FONTES ---
        font_size = int(25 * SCALE) 
        self.font = pygame.font.SysFont("Arial", font_size, bold=True)
        self.padding = int(120 * SCALE) 
        self.btn_size = int(HEIGHT * 0.18) 
        
        self.setup_buttons()
        
        # --- MULTI-TOUCH ---
        self.fingers = {} 
        self.last_shot_time = 0
        self.shoot_delay = 250 

        # --- SISTEMA DE FASES ---
        self.level = 1
        self.total_score = 0
        self.bg_images = []
        self.load_backgrounds()

        self.running = True
        self.new_game()

    def load_backgrounds(self):
        for i in range(1, 6): 
            fname = f'fundo{i}.png'
            path = os.path.join(ASSETS_FOLDER, fname)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert()
                    img = pygame.transform.scale(img, (WIDTH, HEIGHT))
                    self.bg_images.append(img)
                except: pass
        if not self.bg_images:
            path = os.path.join(ASSETS_FOLDER, 'fundo.png')
            if os.path.exists(path):
                img = pygame.image.load(path).convert()
                img = pygame.transform.scale(img, (WIDTH, HEIGHT))
                self.bg_images.append(img)

    def setup_buttons(self):
        # --- DIRECIONAIS ---
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

        # --- BOTÃO TIRO ---
        offset_da_borda = int(100 * SCALE) 
        target_center_x = WIDTH - (self.btn_size // 2) - offset_da_borda
        target_center_y = HEIGHT - (self.btn_size // 2) - int(self.padding * 0.5)
        self.btn_fire_center_point = (target_center_x, target_center_y)

        # Hitbox Grande (1.8x o tamanho base)
        hitbox_size = int(self.btn_size * 1.8) 
        self.btn_fire = pygame.Rect(0, 0, hitbox_size, hitbox_size)
        self.btn_fire.center = self.btn_fire_center_point

        # MENUS
        b_w = int(self.btn_size * 1.5) 
        b_h = int(self.btn_size * 0.6)
        self.btn_weapon = pygame.Rect(WIDTH - b_w - self.padding, int(self.padding * 0.2), b_w, b_h)
        self.btn_char = pygame.Rect(int(self.padding * 0.2), int(self.padding * 0.2), b_w, b_h)

    def new_game(self):
        self.phase_score = 0 
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.flags = pygame.sprite.Group()
        self.bones = pygame.sprite.Group() 
        
        if self.bg_images:
            bg_idx = (self.level - 1) % len(self.bg_images)
            self.current_bg = self.bg_images[bg_idx]
        else:
            self.current_bg = None

        self.create_level_map(difficulty=self.level)
        self.player = Player(self)
        self.all_sprites.add(self.player)

    def create_level_map(self, difficulty=1):
        ground_y = HEIGHT - int(60 * SCALE)
        p = Platform(0, ground_y, int(WIDTH * 1.5), int(60 * SCALE))
        self.all_sprites.add(p)
        self.platforms.add(p)
        
        current_x = int(WIDTH * 1.5)
        min_gap = int(50 * SCALE) + (difficulty * 5)
        max_gap = int(120 * SCALE) + (difficulty * 15) 
        if max_gap > 300 * SCALE: max_gap = 300 * SCALE

        segments = 15 + (difficulty * 2) 
        
        for i in range(segments):
            gap = random.randint(min_gap, max_gap)
            current_x += gap
            
            plat_w = random.randint(int(200 * SCALE), int(500 * SCALE))
            height_variance = int(50 * SCALE) * difficulty
            if height_variance > 250 * SCALE: height_variance = 250 * SCALE
            
            if random.random() > 0.3:
                plat_y = ground_y
            else:
                plat_y = ground_y - random.randint(int(50*SCALE), height_variance)
            
            p = Platform(current_x, plat_y, plat_w, int(60 * SCALE))
            self.all_sprites.add(p)
            self.platforms.add(p)
            
            if random.random() > 0.5:
                num_bones = random.randint(1, 3)
                start_bone_x = current_x + int(50*SCALE)
                for b in range(num_bones):
                    bx = start_bone_x + (b * int(50*SCALE))
                    if bx < current_x + plat_w - int(50*SCALE): 
                        bone = Bone(bx, plat_y)
                        self.all_sprites.add(bone)
                        self.bones.add(bone)

            if random.random() > 0.4:
                etype = random.choice(['gato', 'vaca', 'guarda_chuva'])
                ex = current_x + plat_w // 2
                ey = plat_y - int(150 * SCALE)
                e = Enemy(ex, ey, etype, self, platform=p)
                self.all_sprites.add(e)
                self.enemies.add(e)
            
            current_x += plat_w

        current_x += int(150 * SCALE)
        final_plat = Platform(current_x, ground_y, int(500 * SCALE), int(60 * SCALE))
        self.all_sprites.add(final_plat)
        self.platforms.add(final_plat)
        
        flag = Flag(current_x + int(400 * SCALE), ground_y)
        self.all_sprites.add(flag)
        self.flags.add(flag)

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

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
            for sprite in self.all_sprites:
                if sprite != self.player:
                    sprite.rect.x -= scroll

        hits = pygame.sprite.spritecollide(self.player, self.bones, True)
        for bone in hits: self.total_score += 50 

        if pygame.sprite.spritecollide(self.player, self.flags, False):
            self.total_score += 1000
            self.level += 1 
            self.show_level_screen()
            self.new_game()

        if self.player.rect.top > HEIGHT: self.new_game()

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
            self.level = 1 
            self.total_score = 0
            self.new_game()

    def show_level_screen(self):
        self.screen.fill((0,0,0))
        txt = self.font.render(f"NIVEL {self.level}", True, (255,255,255))
        self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))
        pygame.display.flip()
        pygame.time.delay(2000)

    def draw_transparent_btn(self, rect, text, color=(255, 255, 255)):
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, 150), s.get_rect(), border_radius=15)
        pygame.draw.rect(s, color, s.get_rect(), 2, border_radius=15)
        txt_surf = self.font.render(text, True, color)
        txt_rect = txt_surf.get_rect(center=(rect.width//2, rect.height//2))
        s.blit(txt_surf, txt_rect)
        self.screen.blit(s, rect.topleft)

    def draw_health_bar(self, surface, x, y, pct):
        if pct < 0: pct = 0
        BAR_LENGTH = int(80 * SCALE)
        BAR_HEIGHT = int(8 * SCALE)
        fill = (pct / 100) * BAR_LENGTH
        col = (0, 255, 0) if pct >= 30 else (255, 0, 0)
        pygame.draw.rect(surface, col, (x, y, fill, BAR_HEIGHT))
        pygame.draw.rect(surface, (255, 255, 255), (x, y, BAR_LENGTH, BAR_HEIGHT), 2)

    def draw(self):
        if self.current_bg: self.screen.blit(self.current_bg, (0, 0))
        else: self.screen.fill((135, 206, 235))
            
        self.all_sprites.draw(self.screen)
        
        s_txt = self.font.render(f"SCORE: {self.total_score}", True, (255, 255, 255))
        l_txt = self.font.render(f"NIVEL: {self.level}", True, (255, 255, 0))
        self.screen.blit(s_txt, (WIDTH//2 - s_txt.get_width()//2, 10))
        gap = s_txt.get_height() + 15 
        self.screen.blit(l_txt, (WIDTH//2 - l_txt.get_width()//2, 10 + gap))

        # Controles Esquerda
        self.draw_transparent_btn(self.btn_left, "<")
        self.draw_transparent_btn(self.btn_right, ">")
        self.draw_transparent_btn(self.btn_up, "^")

        # --- BOTÃO TIRO TRANSPARENTE & MAIOR ---
        # 1. Cria superfície transparente quadrada
        # Aumentamos o visual em 20% (multiplicador 1.2)
        visual_size = int(self.btn_size * 1.2) 
        surf = pygame.Surface((visual_size, visual_size), pygame.SRCALPHA)
        
        # 2. Desenha círculo "vidro fumê" (preto alpha 150)
        center = (visual_size // 2, visual_size // 2)
        radius = visual_size // 2
        pygame.draw.circle(surf, (0, 0, 0, 150), center, radius)
        
        # 3. Borda Branca
        pygame.draw.circle(surf, (255, 255, 255), center, radius, 2)
        
        # 4. Texto
        txt = self.font.render("TIRO", True, (255, 255, 255))
        txt_rect = txt.get_rect(center=center)
        surf.blit(txt, txt_rect)
        
        # 5. Coloca na tela (centralizado no ponto alvo)
        final_rect = surf.get_rect(center=self.btn_fire_center_point)
        self.screen.blit(surf, final_rect)

        # Menus
        pygame.draw.rect(self.screen, (50, 50, 50), self.btn_weapon, border_radius=10)
        w_name = WEAPONS_LIST[self.player.weapon_index]['name']
        self.screen.blit(self.font.render(w_name, True, (255, 255, 255)), (self.btn_weapon.x + 10, self.btn_weapon.y + 10))
        
        pygame.draw.rect(self.screen, (50, 100, 50), self.btn_char, border_radius=10)
        c_name = self.player.char_list[self.player.char_index].upper()
        self.screen.blit(self.font.render(c_name, True, (255, 255, 255)), (self.btn_char.x + 10, self.btn_char.y + 10))

        self.draw_health_bar(self.screen, self.player.rect.x, self.player.rect.y - 15, self.player.hp)
        pygame.display.flip()

if __name__ == "__main__":
    g = Game()
    g.run()
