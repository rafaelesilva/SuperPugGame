import pygame
import sys
import os
import random 
from settings import *
from sprites import Player, Platform, Enemy, Explosion, Flag
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
        # Carrega o novo fundo gerado (prioridade para fundo.png)
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
        self.score = 0 
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.flags = pygame.sprite.Group()
        
        self.create_level_map()
        
        self.player = Player(self)
        self.all_sprites.add(self.player)

    def create_level_map(self):
        ground_y = HEIGHT - int(60 * SCALE)
        
        # 1. Área Inicial
        p = Platform(0, ground_y, int(WIDTH * 1.5), int(60 * SCALE))
        self.all_sprites.add(p)
        self.platforms.add(p)
        
        current_x = int(WIDTH * 1.5)
        
        # 2. Gera sequencia de plataformas
        for i in range(20):
            gap = random.randint(int(100 * SCALE), int(250 * SCALE))
            current_x += gap
            
            plat_w = random.randint(int(200 * SCALE), int(500 * SCALE))
            if random.random() > 0.3:
                plat_y = ground_y 
            else:
                plat_y = ground_y - random.randint(int(100 * SCALE), int(200 * SCALE))
            
            p = Platform(current_x, plat_y, plat_w, int(60 * SCALE))
            self.all_sprites.add(p)
            self.platforms.add(p)
            
            if random.random() > 0.4:
                etype = random.choice(['gato', 'vaca', 'guarda_chuva'])
                ex = current_x + plat_w // 2
                ey = plat_y - int(60 * SCALE)
                e = Enemy(ex, ey, etype, self) # Passa 'self' (game) para o inimigo ter gravidade
                self.all_sprites.add(e)
                self.enemies.add(e)
            
            current_x += plat_w

        # 3. Área Final
        current_x += int(150 * SCALE)
        final_plat = Platform(current_x, ground_y, int(500 * SCALE), int(60 * SCALE))
        self.all_sprites.add(final_plat)
        self.platforms.add(final_plat)
        
        flag = Flag(current_x + int(400 * SCALE), ground_y)
        self.all_sprites.add(flag)
        self.flags.add(flag)

    def run(self):
        # --- DEFINIÇÃO DOS BOTÕES ---
        # Botão de TIRO (Canto inferior direito)
        bx_fire = WIDTH - self.btn_size - int(self.padding * 0.5)
        by_fire = HEIGHT - self.btn_size - int(self.padding * 0.5)
        self.btn_fire = pygame.Rect(bx_fire, by_fire, self.btn_size, self.btn_size)
        
        # Botão de PULO (Ao lado do tiro, um pouco mais p/ esquerda)
        bx_jump = bx_fire - self.btn_size - int(20 * SCALE)
        self.btn_jump = pygame.Rect(bx_jump, by_fire + int(20*SCALE), self.btn_size, self.btn_size)
        
        # Botões de Cima (Arma e Personagem)
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

        # Lógica de Segurar (Para andar)
        if mouse_pressed:
            # Só anda se NÃO estiver clicando nos botões de ação
            if not (self.btn_fire.collidepoint(mouse_pos) or 
                    self.btn_jump.collidepoint(mouse_pos) or
                    self.btn_weapon.collidepoint(mouse_pos) or 
                    self.btn_char.collidepoint(mouse_pos)):
                
                # Divide a tela ao meio: Esquerda move Trás, Direita move Frente
                if mouse_pos[0] < WIDTH / 2: touch_left = True
                else: touch_right = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Lógica de Clique Único (Tiro, Pulo, Trocas)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if self.btn_fire.collidepoint((mx, my)):
                    self.shoot()
                elif self.btn_jump.collidepoint((mx, my)):
                    self.player.jump() # PULO AGORA É SÓ AQUI
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
        
        # Câmera
        if self.player.rect.right >= WIDTH * 0.4:
            scroll = self.player.rect.right - (WIDTH * 0.4)
            self.player.rect.right = WIDTH * 0.4 
            for sprite in self.all_sprites:
                if sprite != self.player:
                    sprite.rect.x -= scroll

        # Vitória / Derrota
        if pygame.sprite.spritecollide(self.player, self.flags, False):
            print("VENCEU!!")
            self.score += 1000
            pygame.time.delay(2000)
            self.new_game()

        if self.player.rect.top > HEIGHT:
            self.new_game()

        # Colisões
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, True)
        for enemy, bullets_list in hits.items():
            for b in bullets_list:
                enemy.hp -= b.damage
                if enemy.hp <= 0:
                    expl = Explosion(enemy.rect.center)
                    self.all_sprites.add(expl)
                    enemy.kill()
                    self.score += 100 

        hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        if hits:
            self.player.hp -= 1
            # Empurrão simples
            if self.player.rect.x < hits[0].rect.x: self.player.rect.x -= 20
            else: self.player.rect.x += 20

        if self.player.hp <= 0:
            self.new_game()

    def draw_health_bar(self, surface, x, y, pct):
        if pct < 0: pct = 0
        BAR_LENGTH = int(80 * SCALE)
        BAR_HEIGHT = int(8 * SCALE)
        fill = (pct / 100) * BAR_LENGTH
        pygame.draw.rect(surface, (255,0,0) if pct < 30 else (0,255,0), (x, y, fill, BAR_HEIGHT))
        pygame.draw.rect(surface, WHITE, (x, y, BAR_LENGTH, BAR_HEIGHT), 2)

    def draw(self):
        if self.bg: self.screen.blit(self.bg, (0, 0))
        else: self.screen.fill((135, 206, 235))
            
        self.all_sprites.draw(self.screen)
        
        # --- DESENHA OS BOTÕES ---
        
        # Botão TIRO (Vermelho)
        pygame.draw.circle(self.screen, WHITE, self.btn_fire.center, self.btn_size // 2 + 4)
        pygame.draw.circle(self.screen, (200, 50, 50), self.btn_fire.center, self.btn_size // 2)
        txt = self.font.render("TIRO", True, WHITE)
        self.screen.blit(txt, txt.get_rect(center=self.btn_fire.center))

        # Botão PULO (Verde/Azul)
        pygame.draw.circle(self.screen, WHITE, self.btn_jump.center, self.btn_size // 2 + 4)
        pygame.draw.circle(self.screen, (50, 150, 50), self.btn_jump.center, self.btn_size // 2)
        txt_jump = self.font.render("PULO", True, WHITE)
        self.screen.blit(txt_jump, txt_jump.get_rect(center=self.btn_jump.center))

        # Outros botões e UI
        pygame.draw.rect(self.screen, (50, 50, 50), self.btn_weapon, border_radius=10)
        w_name = WEAPONS_LIST[self.player.weapon_index]['name']
        self.screen.blit(self.font.render(w_name, True, WHITE), (self.btn_weapon.x + 10, self.btn_weapon.y + 10))
        
        pygame.draw.rect(self.screen, (50, 100, 50), self.btn_char, border_radius=10)
        c_name = self.player.char_list[self.player.char_index].upper()
        self.screen.blit(self.font.render(c_name, True, WHITE), (self.btn_char.x + 10, self.btn_char.y + 10))

        self.draw_health_bar(self.screen, self.player.rect.x, self.player.rect.y - 15, self.player.hp)
        
        # Placar
        s_txt = self.font.render(f"SCORE: {self.score}", True, WHITE)
        self.screen.blit(s_txt, (WIDTH//2 - s_txt.get_width()//2, 20))

        pygame.display.flip()

if __name__ == "__main__":
    g = Game()
    g.run()
