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
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        
        font_size = int(25 * SCALE) 
        self.font = pygame.font.SysFont("Arial", font_size, bold=True)
        self.running = True
        
        self.bg = None
        for name in ['fundo.png', 'paisagem.jpg', 'ceu_limpo.png']:
            path = os.path.join(ASSETS_FOLDER, name)
            if os.path.exists(path):
                try:
                    self.bg = pygame.image.load(path).convert()
                    self.bg = pygame.transform.scale(self.bg, (WIDTH, HEIGHT))
                    break
                except: pass

        self.padding = int(120 * SCALE) 
        self.btn_size = int(HEIGHT * 0.18) 
        
        dpad_size = int(80 * SCALE)
        margin = int(20 * SCALE)
        base_y = HEIGHT - dpad_size - margin
        base_x = margin
        self.btn_left = pygame.Rect(base_x, base_y, dpad_size, dpad_size)
        self.btn_right = pygame.Rect(base_x + dpad_size + 10, base_y, dpad_size, dpad_size)
        self.btn_up = pygame.Rect(base_x + (dpad_size // 2) + 5, base_y - dpad_size - 10, dpad_size, dpad_size)

        self.level = 1
        self.total_score = 0
        self.new_game()

    def new_game(self):
        self.phase_score = 0 
        
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.flags = pygame.sprite.Group()
        self.bones = pygame.sprite.Group() 
        
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
        bx_fire = WIDTH - self.btn_size - int(self.padding * 0.5)
        by_fire = HEIGHT - self.btn_size - int(self.padding * 0.5)
        self.btn_fire = pygame.Rect(bx_fire, by_fire, self.btn_size, self.btn_size)
        
        b_w = int(self.btn_size * 1.5) 
        b_h = int(self.btn_size * 0.6)
        self.btn_weapon = pygame.Rect(WIDTH - b_w - self.padding, int(self.padding * 0.2), b_w, b_h)
        self.btn_char = pygame.Rect(int(self.padding * 0.2), int(self.padding * 0.2), b_w, b_h)

        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def events(self):
        touch_left = False
        touch_right = False
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]

        if mouse_pressed:
            if self.btn_left.collidepoint(mouse_pos):
                touch_left = True
            elif self.btn_right.collidepoint(mouse_pos):
                touch_right = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if self.btn_fire.collidepoint((mx, my)):
                    self.shoot()
                elif self.btn_up.collidepoint((mx, my)):
                    self.player.jump()
                elif self.btn_weapon.collidepoint((mx, my)):
                    self.player.weapon_index = (self.player.weapon_index + 1) % len(WEAPONS_LIST)
                elif self.btn_char.collidepoint((mx, my)):
                    self.player.next_character()

        self.player.update_touch(touch_left, touch_right)

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
        for bone in hits:
            self.total_score += 50 

        if pygame.sprite.spritecollide(self.player, self.flags, False):
            print(f"PASSOU O NIVEL {self.level}!")
            self.total_score += 1000
            self.level += 1 
            
            self.screen.fill((0,0,0))
            txt = self.font.render(f"NIVEL {self.level} - PREPARE-SE!", True, (255,255,255))
            self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))
            pygame.display.flip()
            pygame.time.delay(2000)
            
            self.new_game()

        if self.player.rect.top > HEIGHT:
            print("CAIU!")
            self.new_game()

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
            print("GAME OVER")
            self.level = 1 
            self.total_score = 0
            self.new_game()

    def draw_health_bar(self, surface, x, y, pct):
        if pct < 0: pct = 0
        BAR_LENGTH = int(80 * SCALE)
        BAR_HEIGHT = int(8 * SCALE)
        fill = (pct / 100) * BAR_LENGTH
        col = (0, 255, 0) if pct >= 30 else (255, 0, 0)
        pygame.draw.rect(surface, col, (x, y, fill, BAR_HEIGHT))
        pygame.draw.rect(surface, (255, 255, 255), (x, y, BAR_LENGTH, BAR_HEIGHT), 2)

    def draw_transparent_btn(self, rect, text, color=(255, 255, 255)):
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (0, 0, 0, 100), s.get_rect(), border_radius=15)
        pygame.draw.rect(s, color, s.get_rect(), 2, border_radius=15)
        txt_surf = self.font.render(text, True, color)
        txt_rect = txt_surf.get_rect(center=(rect.width//2, rect.height//2))
        s.blit(txt_surf, txt_rect)
        self.screen.blit(s, rect.topleft)

    def draw(self):
        if self.bg: self.screen.blit(self.bg, (0, 0))
        else: self.screen.fill((135, 206, 235))
            
        self.all_sprites.draw(self.screen)
        
        # --- MUDANÇA 2: PLACAR ORGANIZADO ---
        s_txt = self.font.render(f"SCORE: {self.total_score}", True, (255, 255, 255))
        l_txt = self.font.render(f"NIVEL: {self.level}", True, (255, 255, 0))
        
        # Score no topo (y=10)
        self.screen.blit(s_txt, (WIDTH//2 - s_txt.get_width()//2, 10))
        
        # Nível logo abaixo do Score (calculado automaticamente para não sobrepor)
        gap = s_txt.get_height() + 5
        self.screen.blit(l_txt, (WIDTH//2 - l_txt.get_width()//2, 10 + gap))
        # ------------------------------------

        self.draw_transparent_btn(self.btn_left, "<")
        self.draw_transparent_btn(self.btn_right, ">")
        self.draw_transparent_btn(self.btn_up, "^")

        pygame.draw.circle(self.screen, (255, 255, 255), self.btn_fire.center, self.btn_size // 2 + 4)
        pygame.draw.circle(self.screen, (200, 50, 50), self.btn_fire.center, self.btn_size // 2)
        txt = self.font.render("TIRO", True, (255, 255, 255))
        self.screen.blit(txt, txt.get_rect(center=self.btn_fire.center))

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
