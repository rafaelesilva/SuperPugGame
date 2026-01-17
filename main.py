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
        # Define a tela (Full Screen)
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
        self.score = 0 
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        
        # Cria o chão inicial (mais comprido para começar)
        ground_h = int(60 * SCALE)
        # Chão inicial cobre a tela toda
        ground = Platform(0, HEIGHT - ground_h, WIDTH * 2, ground_h)
        self.all_sprites.add(ground)
        self.platforms.add(ground)
        
        # Cria algumas plataformas iniciais
        self.spawn_platform(int(WIDTH * 0.5), int(WIDTH * 0.8))
        self.spawn_platform(int(WIDTH * 0.9), int(WIDTH * 1.2))
        
        self.player = Player(self)
        self.all_sprites.add(self.player)
        
        # Spawna inimigo inicial
        self.spawn_enemy()

    def spawn_platform(self, min_x, max_x):
        # Cria uma plataforma em um lugar aleatório dentro da faixa X
        w = int(random.randint(150, 300) * SCALE)
        h = int(30 * SCALE)
        x = random.randint(min_x, max_x)
        y = random.randint(int(HEIGHT * 0.4), int(HEIGHT * 0.75))
        
        p = Platform(x, y, w, h)
        self.all_sprites.add(p)
        self.platforms.add(p)

    def spawn_enemy(self):
        # Inimigos nascem fora da tela (na direita)
        etype = random.choice(['gato', 'vaca', 'guarda_chuva'])
        x = WIDTH + random.randint(100, 300)
        y = HEIGHT - int(120 * SCALE)
        if etype == 'guarda_chuva': y -= int(150 * SCALE)
        
        e = Enemy(x, y, etype)
        self.all_sprites.add(e)
        self.enemies.add(e)

    def run(self):
        # Posicionamento dos botões
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
        
        # --- LÓGICA DA CÂMERA (SCROLL) ---
        # Se o jogador chegar no meio da tela (lado direito), o mundo anda pra trás
        if self.player.rect.right >= WIDTH / 2:
            # A diferença é o quanto ele "passou" do meio
            scroll = self.player.rect.right - (WIDTH / 2)
            self.player.rect.right = WIDTH / 2 # Trava o jogador no meio
            
            # Move TUDO para a esquerda
            for plat in self.platforms:
                plat.rect.x -= scroll
                # Se a plataforma sair da tela pela esquerda, deleta ela
                if plat.rect.right < 0:
                    plat.kill()

            for enemy in self.enemies:
                enemy.rect.x -= scroll
                
            for bullet in self.bullets:
                bullet.rect.x -= scroll
                
            # GERAÇÃO INFINITA DE PLATAFORMAS
            # Se tiver poucas plataformas (menos de 5), cria mais na frente
            if len(self.platforms) < 5:
                # Cria uma nova plataforma lá na direita (fora da tela)
                self.spawn_platform(WIDTH, WIDTH + 200)

            # GERAÇÃO INFINITA DE INIMIGOS
            if len(self.enemies) < 2: # Mantém sempre 1 ou 2 inimigos vindo
                if random.randint(0, 100) < 2: # Pequena chance a cada frame
                    self.spawn_enemy()

        # --- FIM DA CÂMERA ---

        # Colisões (Tiro x Inimigo)
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, True)
        for enemy, bullets_list in hits.items():
            for b in bullets_list:
                enemy.hp -= b.damage
                if enemy.hp <= 0:
                    expl = Explosion(enemy.rect.center)
                    self.all_sprites.add(expl)
                    enemy.kill()
                    self.score += 100 

        # Colisão (Inimigo x Jogador)
        hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        if hits:
            self.player.hp -= 1
            for enemy in hits:
                if enemy.rect.centerx > self.player.rect.centerx:
                    enemy.rect.x += int(30 * SCALE)
                else:
                    enemy.rect.x -= int(30 * SCALE)

        # Game Over e Queda no Abismo
        if self.player.hp <= 0 or self.player.rect.top > HEIGHT:
            print(f"GAME OVER! Score Final: {self.score}")
            self.new_game()

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
        
        # Botões
        pygame.draw.circle(self.screen, WHITE, self.btn_fire.center, self.btn_size // 2 + 3)
        s_fire = pygame.Surface((self.btn_size, self.btn_size), pygame.SRCALPHA)
        pygame.draw.circle(s_fire, (255, 0, 0, 200), (self.btn_size//2, self.btn_size//2), self.btn_size // 2)
        self.screen.blit(s_fire, self.btn_fire.topleft)
        txt = self.font.render("TIRO", True, WHITE)
        self.screen.blit(txt, txt.get_rect(center=self.btn_fire.center))

        pygame.draw.rect(self.screen, WHITE, self.btn_weapon.inflate(6,6), border_radius=12)
        pygame.draw.rect(self.screen, (50, 50, 50), self.btn_weapon, border_radius=12)
        w_name = WEAPONS_LIST[self.player.weapon_index]['name']
        txt_w = self.font.render(w_name, True, WHITE)
        self.screen.blit(txt_w, txt_w.get_rect(center=self.btn_weapon.center))
        
        pygame.draw.rect(self.screen, WHITE, self.btn_char.inflate(6,6), border_radius=12)
        pygame.draw.rect(self.screen, (50, 100, 50), self.btn_char, border_radius=12)
        c_name = self.player.char_list[self.player.char_index].upper()
        txt_c = self.font.render(c_name, True, WHITE)
        self.screen.blit(txt_c, txt_c.get_rect(center=self.btn_char.center))

        # UI: Vida e Placar
        self.draw_health_bar(self.screen, self.player.rect.x - 10, self.player.rect.y - 15, self.player.hp)

        score_text = self.font.render(f"SCORE: {self.score}", True, WHITE)
        score_shadow = self.font.render(f"SCORE: {self.score}", True, BLACK)
        cx = WIDTH // 2
        cy = int(20 * SCALE)
        self.screen.blit(score_shadow, (cx - score_text.get_width()//2 + 2, cy + 2))
        self.screen.blit(score_text, (cx - score_text.get_width()//2, cy))

        pygame.display.flip()

if __name__ == "__main__":
    g = Game()
    g.run()
