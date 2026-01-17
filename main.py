import pygame
import sys
import os
import random 
from settings import *
from sprites import Player, Platform, Enemy, Explosion 
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
        for name in ['fundo.png', 'paisagem.jpg']:
            path = os.path.join(ASSETS_FOLDER, name)
            if os.path.exists(path):
                try:
                    self.bg = pygame.image.load(path).convert()
                    self.bg = pygame.transform.scale(self.bg, (WIDTH, HEIGHT))
                    break
                except: pass

        self.padding = int(120 * SCALE) 
        self.btn_size = int(HEIGHT * 0.18) 

        self.new_game()

    def new_game(self):
        self.score = 0 # Inicia pontuação zerada
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        
        ground_h = int(60 * SCALE)
        ground = Platform(0, HEIGHT - ground_h, WIDTH, ground_h)
        self.all_sprites.add(ground)
        self.platforms.add(ground)
        
        plat_w = int(200 * SCALE)
        plat_h = int(30 * SCALE)
        p1 = Platform(int(200 * SCALE), HEIGHT - int(250 * SCALE), plat_w, plat_h)
        self.all_sprites.add(p1)
        self.platforms.add(p1)
        
        self.spawn_enemy()
        self.spawn_enemy()

        self.player = Player(self)
        self.all_sprites.add(self.player)

    def spawn_enemy(self):
        etype = random.choice(['gato', 'vaca', 'guarda_chuva'])
        x = random.randint(WIDTH + 50, WIDTH + 300)
        y = HEIGHT - int(120 * SCALE)
        if etype == 'guarda_chuva': y -= int(150 * SCALE)
        
        e = Enemy(x, y, etype)
        self.all_sprites.add(e)
        self.enemies.add(e)

    def run(self):
        bx = WIDTH - self.btn_size - int(self.padding * 0.8) 
        by = HEIGHT - self.btn_size - int(self.padding * 0.6) 
        self.btn_fire = pygame.Rect(bx, by, self.btn_size, self.btn_size)
        
        b_w = int(self.btn_size * 1.5) 
        b_h = int(self.btn_size * 0.6)
        self.btn_weapon = pygame.Rect(WIDTH - b_w - self.padding, int(self.padding * 0.5), b_w, b_h)
        self.btn_char = pygame.Rect(int(self.padding * 0.5), int(self.padding * 0.5), b_w, b_h)

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
            if not (self.btn_fire.collidepoint(mouse_pos) or 
                    self.btn_weapon.collidepoint(mouse_pos) or 
                    self.btn_char.collidepoint(mouse_pos)):
                if mouse_pos[0] < WIDTH / 2: touch_left = True
                else: touch_right = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if self.btn_fire.collidepoint((mx, my)):
                    self.shoot()
                elif self.btn_weapon.collidepoint((mx, my)):
                    self.player.weapon_index = (self.player.weapon_index + 1) % len(WEAPONS_LIST)
                elif self.btn_char.collidepoint((mx, my)):
                    self.player.next_character()
                elif not (self.btn_weapon.collidepoint((mx,my)) or self.btn_char.collidepoint((mx,my))):
                    self.player.jump()

        self.player.update_touch(touch_left, touch_right)

    def shoot(self):
        dir = 1 if self.player.facing_right else -1
        b = Projectile(self.player.rect.centerx, self.player.rect.centery, dir, self.player.weapon_index)
        self.all_sprites.add(b)
        self.bullets.add(b)

    def update(self):
        self.all_sprites.update()
        
        # 1. Colisão: Bala mata Inimigo (Score)
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, True)
        for enemy, bullets_list in hits.items():
            for b in bullets_list:
                enemy.hp -= b.damage
                if enemy.hp <= 0:
                    expl = Explosion(enemy.rect.center)
                    self.all_sprites.add(expl)
                    enemy.kill()
                    self.score += 100 # Ganha 100 pontos!
                    self.spawn_enemy()

        # 2. Colisão: Inimigo acerta Jogador (Dano)
        hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        if hits:
            # Tira vida
            self.player.hp -= 2 # Dano do inimigo
            
            # Efeito de empurrão (Knockback) para não morrer instantâneo
            for enemy in hits:
                if enemy.rect.centerx > self.player.rect.centerx:
                    enemy.rect.x += int(30 * SCALE)
                else:
                    enemy.rect.x -= int(30 * SCALE)

        # 3. Game Over (Se vida acabar, reinicia)
        if self.player.hp <= 0:
            print(f"GAME OVER! Score Final: {self.score}")
            self.new_game()

        for e in self.enemies:
            if e.rect.right < -100:
                e.kill()
                self.spawn_enemy()

    # Função auxiliar para desenhar a barrinha
    def draw_health_bar(self, surface, x, y, pct):
        if pct < 0: pct = 0
        BAR_LENGTH = int(80 * SCALE)
        BAR_HEIGHT = int(8 * SCALE)
        fill = (pct / 100) * BAR_LENGTH
        outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
        fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
        
        col = GREEN
        if pct < 30: col = RED
        
        pygame.draw.rect(surface, col, fill_rect)
        pygame.draw.rect(surface, WHITE, outline_rect, 2)

    def draw(self):
        if self.bg:
            self.screen.blit(self.bg, (0, 0))
        else:
            self.screen.fill((100, 200, 255))
            
        self.all_sprites.draw(self.screen)
        
        # --- UI E BOTÕES ---
        # Botão Tiro
        pygame.draw.circle(self.screen, WHITE, self.btn_fire.center, self.btn_size // 2 + 3)
        s_fire = pygame.Surface((self.btn_size, self.btn_size), pygame.SRCALPHA)
        pygame.draw.circle(s_fire, (255, 0, 0, 200), (self.btn_size//2, self.btn_size//2), self.btn_size // 2)
        self.screen.blit(s_fire, self.btn_fire.topleft)
        txt = self.font.render("TIRO", True, WHITE)
        self.screen.blit(txt, txt.get_rect(center=self.btn_fire.center))

        # Botão Arma
        pygame.draw.rect(self.screen, WHITE, self.btn_weapon.inflate(6,6), border_radius=12)
        pygame.draw.rect(self.screen, (50, 50, 50), self.btn_weapon, border_radius=12)
        w_name = WEAPONS_LIST[self.player.weapon_index]['name']
        txt_w = self.font.render(w_name, True, WHITE)
        self.screen.blit(txt_w, txt_w.get_rect(center=self.btn_weapon.center))
        
        # Botão Personagem
        pygame.draw.rect(self.screen, WHITE, self.btn_char.inflate(6,6), border_radius=12)
        pygame.draw.rect(self.screen, (50, 100, 50), self.btn_char, border_radius=12)
        c_name = self.player.char_list[self.player.char_index].upper()
        txt_c = self.font.render(c_name, True, WHITE)
        self.screen.blit(txt_c, txt_c.get_rect(center=self.btn_char.center))

        # --- NOVA UI (VIDA E PLACAR) ---
        # Barra de Vida (em cima do jogador)
        self.draw_health_bar(self.screen, self.player.rect.x - 10, self.player.rect.y - 15, self.player.hp)

        # Placar (Topo Centro)
        score_text = self.font.render(f"SCORE: {self.score}", True, WHITE)
        # Sombra preta para leitura
        score_shadow = self.font.render(f"SCORE: {self.score}", True, BLACK)
        
        cx = WIDTH // 2
        cy = int(20 * SCALE)
        self.screen.blit(score_shadow, (cx - score_text.get_width()//2 + 2, cy + 2))
        self.screen.blit(score_text, (cx - score_text.get_width()//2, cy))

        pygame.display.flip()

if __name__ == "__main__":
    g = Game()
    g.run()
